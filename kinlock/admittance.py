"""
KINLOCK Admittance Controller & Active Hold State Machine.
Regulates deceleration dynamics during emergency stops and maintains workpiece
equilibrium without torque drops.
"""

import time
import numpy as np
from typing import Tuple
from .models import GovernorState, StepTelemetry


class AdmittanceController:
    """
    Coordinates safe robotic deceleration and active admittance clamping when
    interrupt triggers are received from the acoustic reflex or operator input.
    """

    def __init__(self, damping_ratio: float = 0.85, emergency_decel_rad_s2: float = 8.0):
        self.damping_ratio = damping_ratio
        self.emergency_decel = emergency_decel_rad_s2
        self.is_abort_latched = False
        self.abort_timestamp_ms = 0.0
        self.initial_abort_q_dot = None

    def trigger_acoustic_abort(self, timestamp_ms: float = 0.0):
        """Latches the system into ACOUSTIC_ABORT state."""
        self.is_abort_latched = True
        self.abort_timestamp_ms = timestamp_ms if timestamp_ms > 0 else time.time() * 1000.0

    def reset_abort(self):
        """Clears the abort latch."""
        self.is_abort_latched = False
        self.initial_abort_q_dot = None

    def compute_governed_action(
        self,
        q_dot_governed: np.ndarray,
        dt: float = 0.01,
        current_time_ms: float = 0.0
    ) -> Tuple[np.ndarray, GovernorState]:
        """
        Filters the joint velocity. If acoustic abort is triggered, smoothly decelerates
        all joint velocities to 0.0 rad/s while maintaining rigid gripper clamping.
        """
        if not self.is_abort_latched:
            return q_dot_governed, GovernorState.NOMINAL_TRACKING

        # In abort state: apply exponential deceleration curve to zero
        if self.initial_abort_q_dot is None:
            self.initial_abort_q_dot = q_dot_governed.copy()

        if current_time_ms > 0 and self.abort_timestamp_ms > 0 and current_time_ms >= self.abort_timestamp_ms:
            elapsed_s = (current_time_ms - self.abort_timestamp_ms) / 1000.0
        elif current_time_ms > 0:
            elapsed_s = current_time_ms / 1000.0
        else:
            elapsed_s = dt

        # Exponential decay envelope: v(t) = v0 * exp(-decel * t)
        decay = float(np.exp(-self.emergency_decel * elapsed_s))
        q_dot_decelerated = self.initial_abort_q_dot * decay

        if np.max(np.abs(q_dot_decelerated)) < 1e-4:
            q_dot_decelerated = np.zeros_like(q_dot_decelerated)

        return q_dot_decelerated, GovernorState.ACOUSTIC_ABORT
