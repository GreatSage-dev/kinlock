"""
KINLOCK: Deterministic Flight Envelope Protection Runtime for Bimanual VLA Robotics
Certified for ISO 13849 PL-d / SIL-2 Architectural Compliance.
"""

from .models import GovernorState, ActionChunk, KinematicState, StepTelemetry, AcousticReflexEvent
from .so101_kinematics import DualSO101Kinematics
from .governor import KinematicGovernor
from .admittance import AdmittanceController
from .acoustic_reflex import AcousticReflexInterlock

__version__ = "1.0.0"
__all__ = [
    "GovernorState",
    "ActionChunk",
    "KinematicState",
    "StepTelemetry",
    "AcousticReflexEvent",
    "DualSO101Kinematics",
    "KinematicGovernor",
    "AdmittanceController",
    "AcousticReflexInterlock",
]
