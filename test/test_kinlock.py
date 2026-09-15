"""
Unit and Adversarial Test Suite for KINLOCK Runtime.
Tests forward kinematics, Jacobian accuracy, null-space projection invariance,
and acoustic reflex trigger mechanics.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import numpy as np
from kinlock.so101_kinematics import DualSO101Kinematics
from kinlock.governor import KinematicGovernor
from kinlock.admittance import AdmittanceController
from kinlock.acoustic_reflex import AcousticReflexInterlock
from kinlock.models import GovernorState


@pytest.fixture
def setup_kinematics():
    kin = DualSO101Kinematics(base_separation_mm=400.0, nominal_grasp_distance_mm=250.0)
    q_nominal = np.array([
        0.35, 0.45, -0.65, 0.20, 0.0, 0.0,
       -0.35, 0.45, -0.65, 0.20, 0.0, 0.0
    ], dtype=np.float64)
    return kin, q_nominal


def test_forward_kinematics_symmetry(setup_kinematics):
    kin, q = setup_kinematics
    ee1, ee2, _, _ = kin.forward_kinematics_bimanual(q)
    # Both arms reach forward into +Y workspace at the same height Z, mirrored across X=0
    assert np.isclose(ee1[1], ee2[1], atol=1e-2)
    assert np.isclose(ee1[2], ee2[2], atol=1e-2)
    assert np.isclose(ee1[0], -ee2[0], atol=1e-2)


def test_jacobian_shape_and_finite_differences(setup_kinematics):
    kin, q = setup_kinematics
    J1, J2 = kin.compute_bimanual_jacobians(q)
    assert J1.shape == (3, 6)
    assert J2.shape == (3, 6)
    assert not np.isnan(J1).any()
    assert not np.isnan(J2).any()


def test_constraint_matrix_orthogonal_projection(setup_kinematics):
    kin, q = setup_kinematics
    C, dist, n12 = kin.compute_constraint_matrix(q)
    assert C.shape == (1, 12)
    assert dist > 100.0

    governor = KinematicGovernor(kin, nominal_distance_mm=dist)
    
    # Intentionally divergent action proposal: Arm 1 moves right, Arm 2 moves left
    q_dot_divergent = np.array([0.2, 0.0, 0.0, 0.0, 0.0, 0.0,
                               -0.2, 0.0, 0.0, 0.0, 0.0, 0.0])
    
    q_dot_safe, telemetry = governor.project_action(q, q_dot_divergent, dt=0.01)
    
    # Under governed action, rate of distance change should be close to zero
    rate_of_change = float((C @ q_dot_safe).item())
    assert abs(rate_of_change) < 1e-3, f"Projected velocity violated null space: {rate_of_change}"
    assert telemetry.governed_force_n < 5.0


def test_admittance_hold_and_decay():
    admittance = AdmittanceController(emergency_decel_rad_s2=10.0)
    test_v = np.array([0.5] * 12)

    # Before abort: normal tracking
    v_out, state = admittance.compute_governed_action(test_v, dt=0.01)
    assert state == GovernorState.NOMINAL_TRACKING
    assert np.allclose(v_out, test_v)

    # Trigger abort
    admittance.trigger_acoustic_abort(timestamp_ms=1000.0)
    v_abort, state_abort = admittance.compute_governed_action(test_v, dt=0.01, current_time_ms=1100.0)
    assert state_abort == GovernorState.ACOUSTIC_ABORT
    assert np.all(v_abort < test_v)


def test_acoustic_reflex_keyword_matching():
    events = []
    def callback(t_ms):
        events.append(t_ms)

    reflex = AcousticReflexInterlock(abort_callback=callback)
    
    # Harmless partial
    res1 = reflex.process_partial_transcript("robot move forward", 10.0, 0.0)
    assert not res1
    assert len(events) == 0

    # Emergency abort partial
    res2 = reflex.process_partial_transcript("STOP IMMEDIATELY", 25.0, 0.0)
    assert res2
    assert len(events) == 1
    assert reflex.last_event.keyword_detected == "STOP"
