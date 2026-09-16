"""
Dual SO-101 Analytical Kinematics and Jacobian Engine.
Based on Hugging Face LeRobot BiSOFollower 6-DOF mechanical parameters.
Computes Forward Kinematics (FK), Cartesian Jacobians, and the Closed-Chain Constraint Matrix C(q).
"""

import numpy as np
from typing import Tuple


class DualSO101Kinematics:
    """
    Kinematic model for two coupled SO-101 6-DOF arms sharing a common coordinate frame.
    Base positions are mounted symmetrically on the table workbench along the X axis.
    """

    def __init__(self, base_separation_mm: float = 400.0, nominal_grasp_distance_mm: float = 348.24):
        self.base_separation_mm = base_separation_mm
        self.nominal_grasp_distance_mm = nominal_grasp_distance_mm

        # Base offsets in world frame (mm)
        self.base1 = np.array([-base_separation_mm / 2.0, 0.0, 0.0], dtype=np.float64)
        self.base2 = np.array([ base_separation_mm / 2.0, 0.0, 0.0], dtype=np.float64)

        # SO-101 Link lengths (mm) from CAD / LeRobot spec
        self.l_base = 65.0       # Base height
        self.l_upper = 125.0     # Upper arm
        self.l_forearm = 135.0   # Forearm
        self.l_wrist = 70.0      # Wrist pitch link
        self.l_tool = 60.0       # Gripper center of grasp

        # Joint limits in radians [-pi, pi]
        self.q_min = np.array([-2.6, -1.8, -1.8, -1.8, -3.1, -1.5] * 2, dtype=np.float64)
        self.q_max = np.array([ 2.6,  1.8,  1.8,  1.8,  3.1,  1.5] * 2, dtype=np.float64)

    def forward_kinematics_single(self, q: np.ndarray, base_pos: np.ndarray, is_left: bool = True) -> Tuple[np.ndarray, list]:
        """
        Compute forward kinematics for a single 6-DOF SO-101 arm.
        Returns end-effector position (3,) and list of intermediate joint positions for visualization.
        """
        q1, q2, q3, q4, q5, q6 = q

        # Inward facing base rotation: Right arm (is_left=False) is mounted facing 180 deg toward center
        yaw_offset = 0.0 if is_left else np.pi
        yaw_total = q1 + yaw_offset

        # Joint 1: Base Yaw rotation around Z
        c1, s1 = np.cos(yaw_total), np.sin(yaw_total)
        p0 = base_pos
        p1 = p0 + np.array([0.0, 0.0, self.l_base])

        # Pitch angles in the sagittal plane
        theta2 = q2
        theta23 = q2 + q3
        theta234 = q2 + q3 + q4

        # In-plane reach (r) and vertical height (z)
        r2 = self.l_upper * np.sin(theta2)
        z2 = self.l_upper * np.cos(theta2)
        p2 = p1 + np.array([r2 * c1, r2 * s1, z2])

        r3 = r2 + self.l_forearm * np.sin(theta23)
        z3 = z2 + self.l_forearm * np.cos(theta23)
        p3 = p1 + np.array([r3 * c1, r3 * s1, z3])

        r4 = r3 + self.l_wrist * np.sin(theta234)
        z4 = z3 + self.l_wrist * np.cos(theta234)
        p4 = p1 + np.array([r4 * c1, r4 * s1, z4])

        # Tool position extends along the wrist vector
        r5 = r4 + self.l_tool * np.sin(theta234)
        z5 = z4 + self.l_tool * np.cos(theta234)
        ee_pos = p1 + np.array([r5 * c1, r5 * s1, z5])

        joint_chain = [p0, p1, p2, p3, p4, ee_pos]
        return ee_pos, joint_chain

    def forward_kinematics_bimanual(self, q: np.ndarray) -> Tuple[np.ndarray, np.ndarray, list, list]:
        """
        Compute positions for both arms.
        q has shape (12,) -> q[:6] for Arm 1, q[6:] for Arm 2.
        """
        q1 = q[:6]
        q2 = q[6:]
        ee1, chain1 = self.forward_kinematics_single(q1, self.base1, is_left=True)
        ee2, chain2 = self.forward_kinematics_single(q2, self.base2, is_left=False)
        return ee1, ee2, chain1, chain2

    def compute_jacobian_single(self, q: np.ndarray, base_pos: np.ndarray, is_left: bool = True, delta: float = 1e-6) -> np.ndarray:
        """
        Compute 3x6 Cartesian linear velocity Jacobian via central difference.
        J_ij = d(pos_i) / d(q_j).
        """
        J = np.zeros((3, 6), dtype=np.float64)
        for i in range(6):
            q_plus = q.copy()
            q_minus = q.copy()
            q_plus[i] += delta
            q_minus[i] -= delta

            pos_plus, _ = self.forward_kinematics_single(q_plus, base_pos, is_left=is_left)
            pos_minus, _ = self.forward_kinematics_single(q_minus, base_pos, is_left=is_left)
            J[:, i] = (pos_plus - pos_minus) / (2.0 * delta)
        return J

    def compute_bimanual_jacobians(self, q: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Returns (J1, J2) each of shape (3, 6)."""
        J1 = self.compute_jacobian_single(q[:6], self.base1, is_left=True)
        J2 = self.compute_jacobian_single(q[6:], self.base2, is_left=False)
        return J1, J2

    def compute_constraint_matrix(self, q: np.ndarray) -> Tuple[np.ndarray, float, np.ndarray]:
        """
        Computes the 1x12 closed-chain kinematic constraint matrix C(q):
        C(q) * q_dot = d/dt(||ee1 - ee2||) = n_12^T * (J1 * q_dot_1 - J2 * q_dot_2) = 0.
        Returns:
            C: shape (1, 12)
            distance_mm: current separation distance
            n12: unit direction vector from ee2 to ee1
        """
        ee1, ee2, _, _ = self.forward_kinematics_bimanual(q)
        disp = ee1 - ee2
        dist = np.linalg.norm(disp)
        if dist < 1e-6:
            n12 = np.array([1.0, 0.0, 0.0], dtype=np.float64)
        else:
            n12 = disp / dist

        J1, J2 = self.compute_bimanual_jacobians(q)

        # C_1 = n12^T * J1  (shape 1x6)
        # C_2 = -n12^T * J2 (shape 1x6)
        C1 = n12.reshape(1, 3) @ J1
        C2 = -n12.reshape(1, 3) @ J2

        C = np.hstack([C1, C2])  # Shape (1, 12)
        return C, dist, n12
