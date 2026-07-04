from enum import Enum


class ErrorClassification(str, Enum):
    TRANSIENT = "transient"
    PERMANENT = "permanent"


class OutreachForgeError(Exception):
    classification: ErrorClassification = ErrorClassification.PERMANENT


class ExternalAPIError(OutreachForgeError):
    classification = ErrorClassification.TRANSIENT


class PermanentFailure(OutreachForgeError):
    classification = ErrorClassification.PERMANENT


class CircuitOpenError(OutreachForgeError):
    classification = ErrorClassification.TRANSIENT
