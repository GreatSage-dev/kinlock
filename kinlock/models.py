"""
KINLOCK Data Models & Telemetry Schemas
Defines structured immutable records for the bimanual kinematic governor,
safety telemetry, and acoustic reflex state machine.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import numpy as np


class GovernorState(str, Enum):
    NOMINAL_TRACKING = "NOMINAL_TRACKING"
    ENVELOPE_CLAMPED = "ENVELOPE_CLAMPED"
    ACOUSTIC_ABORT = "ACOUSTIC_ABORT"
    EMERGENCY_LOCK = "EMERGENCY_LOCK"


@dataclass
class ActionChunk:
    """Represents a 12-DOF joint velocity proposal emitted by a VLA policy."""
    chunk_id: int
    timestamp_ns: int
    q_dot_proposed: np.ndarray  # Shape (12,)
    inference_latency_ms: float
    confidence_score: float = 0.95

    def __post_init__(self):
        if not isinstance(self.q_dot_proposed, np.ndarray):
            self.q_dot_proposed = np.array(self.q_dot_proposed, dtype=np.float64)
        assert self.q_dot_proposed.shape == (12,), f"Expected 12-DOF action, got {self.q_dot_proposed.shape}"


@dataclass
class KinematicState:
    """Instantaneous state of the dual SO-101 bimanual arms."""
    q: np.ndarray             # Shape (12,) - Joint angles [Arm1(6), Arm2(6)]
    q_dot: np.ndarray         # Shape (12,) - Joint velocities
    ee1_pos: np.ndarray       # Shape (3,)  - Arm 1 End-Effector position (mm)
    ee2_pos: np.ndarray       # Shape (3,)  - Arm 2 End-Effector position (mm)
    grasp_distance_mm: float  # Euclidean distance between end-effectors
    distance_error_mm: float  # ||ee1 - ee2|| - L_target
    internal_force_n: float   # Calculated tension/compression force (N)
    timestamp_ms: float


@dataclass
class AcousticReflexEvent:
    """Acoustic trigger event emitted by Speechmatics streaming partials."""
    keyword_detected: str
    detection_latency_ms: float
    source_audio_timestamp_ms: float
    confidence: float
    preempted_action_id: int


@dataclass
class StepTelemetry:
    """Per-step audit receipt verifying physical constraint enforcement."""
    step: int
    raw_divergence_force_n: float     # What force WOULD have been without KINLOCK
    governed_force_n: float            # Actual force with KINLOCK active
    projection_latency_us: float       # Microseconds to solve null-space projection
    state: GovernorState
    constraint_violation_prevented: bool
    ee1_pos: List[float]
    ee2_pos: List[float]
    q_dot_safe: List[float]
