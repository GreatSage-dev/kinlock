"""
KINLOCK Null-Space Closed-Chain Kinematic Governor.
Projects unconstrained 12-DOF VLA action proposals onto the null-space of rigid
closed-chain constraints (C(q) * q_dot = 0) with Baumgarte drift stabilization.
"""

import time
import numpy as np
from typing import Tuple
from .models import GovernorState, KinematicState, StepTelemetry
from .so101_kinematics import DualSO101Kinematics


class KinematicGovernor:
    """
    Sub-millisecond mathematical safety governor enforcing Closed-Chain Kinematic Invariance
    and Flight Envelope Protection for bimanual robotic manipulation.
    """

    def __init__(
        self,
        kinematics: DualSO101Kinematics,
        nominal_distance_mm: float = 250.0,
        max_allowed_internal_force_n: float = 15.0,
        k_servo_n_per_mm: float = 80.0,
        k_object_n_per_mm: float = 60.0,
        drift_damping_alpha: float = 12.0,
        max_joint_velocity_rad_s: float = 1.5
    ):
        self.kin = kinematics
        self.nominal_distance_mm = nominal_distance_mm
        self.max_allowed_force_n = max_allowed_internal_force_n
        self.drift_damping_alpha = drift_damping_alpha
        self.max_q_dot = max_joint_velocity_rad_s

        # Effective series contact stiffness (N/mm) - Tier C Scoped Parameter
        self.k_effective = (k_servo_n_per_mm * k_object_n_per_mm) / (k_servo_n_per_mm + k_object_n_per_mm)

        # State tracking
        self.current_state = GovernorState.NOMINAL_TRACKING
        self.total_violations_prevented = 0
        self.history = []

    def compute_internal_force(self, current_distance_mm: float) -> float:
        """
        Calculates internal tensile/compressive force from distance error using Hooke's effective stiffness.
        F = k_eff * |r - L_target|
        """
        error_mm = abs(current_distance_mm - self.nominal_distance_mm)
        return self.k_effective * error_mm

    def project_action(self, q: np.ndarray, q_dot_vla: np.ndarray, dt: float = 0.01) -> Tuple[np.ndarray, StepTelemetry]:
        """
        Projects unconstrained VLA joint velocity proposal onto the closed-chain null space.
        Returns:
            q_dot_safe: Shape (12,)
            telemetry: StepTelemetry record documenting physical force before/after
        """
        t0 = time.perf_counter_ns()

        # 1. Compute current kinematic state & constraint matrix C(q)
        C, current_dist, n12 = self.kin.compute_constraint_matrix(q)
        dist_error = current_dist - self.nominal_distance_mm

        # 2. Compute what the raw VLA proposal WOULD do to distance & force (Unfiltered baseline)
        q_raw_next = q + q_dot_vla * dt
        _, raw_next_dist, _ = self.kin.compute_constraint_matrix(q_raw_next)
        raw_force = self.compute_internal_force(raw_next_dist)

        # 3. Formulate null-space projection with Baumgarte drift stabilization:
        # We desire d/dt(r) = -alpha * (r - r_nominal) to actively pull any error to zero
        desired_dr_dt = -self.drift_damping_alpha * dist_error

        c_dot_actual = float((C @ q_dot_vla).item())
        c_norm_sq = float((C @ C.T).item())

        if c_norm_sq > 1e-9:
            # Closed-form Moore-Penrose projection with drift compensation
            correction_scalar = (c_dot_actual - desired_dr_dt) / c_norm_sq
            q_dot_safe = q_dot_vla - (C.T * correction_scalar).flatten()
        else:
            q_dot_safe = q_dot_vla.copy()

        # 4. Joint limit velocity saturation
        q_dot_safe = np.clip(q_dot_safe, -self.max_q_dot, self.max_q_dot)

        # 5. Measure resulting force under governed action
        q_safe_next = q + q_dot_safe * dt
        _, safe_next_dist, _ = self.kin.compute_constraint_matrix(q_safe_next)
        governed_force = self.compute_internal_force(safe_next_dist)

        # 6. Assess governor action: flag if projection modified unconstrained action
        violation_prevented = False
        action_modified = bool(np.linalg.norm(q_dot_safe - q_dot_vla) > 1e-3)
        if action_modified or (raw_force > self.max_allowed_force_n):
            violation_prevented = True
            self.total_violations_prevented += 1
            self.current_state = GovernorState.ENVELOPE_CLAMPED
        elif self.current_state != GovernorState.ACOUSTIC_ABORT:
            self.current_state = GovernorState.NOMINAL_TRACKING

        t1 = time.perf_counter_ns()
        projection_us = (t1 - t0) / 1000.0

        ee1, ee2, _, _ = self.kin.forward_kinematics_bimanual(q)
        step_id = len(self.history) + 1

        telemetry = StepTelemetry(
            step=step_id,
            raw_divergence_force_n=float(raw_force),
            governed_force_n=float(governed_force),
            projection_latency_us=float(projection_us),
            state=self.current_state,
            constraint_violation_prevented=violation_prevented,
            ee1_pos=ee1.tolist(),
            ee2_pos=ee2.tolist(),
            q_dot_safe=q_dot_safe.tolist()
        )
        self.history.append(telemetry)

        return q_dot_safe, telemetry
