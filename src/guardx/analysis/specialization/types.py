"""Type definitions for specialization analysis."""
from enum import Enum


class SpecializationAnalysisType(str, Enum):
    """Enumeration of specialization analysis types."""

    FUNCTIONS = "functions"
    SYSCALLS = "system_calls"
    CAPABILITIES = "capabilities"

    def __str__(self) -> str:
        return str(self.value)
