"""Define types for the analysis package."""
from enum import Enum
from typing import Dict, List


class AnalysisType(str, Enum):
    """Enumeration of analysis types."""

    SPECIALIZATION = "specialization"
    DETECT_SECRET = "detect_secrets"
    UNSAFE_CODE = "unsafe_code"

    def __str__(self) -> str:
        return str(self.value)


class AnalysisResults(Dict):
    """Analysis summary dictionary."""

    def get_specialization_results(self) -> List[str]:
        """Return list of specialization results for the program."""
        return self[AnalysisType.SPECIALIZATION] if AnalysisType.SPECIALIZATION in self else None


class AnalysisSensitivity(str, Enum):
    """Enumeration of analysis sensitivity levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    def __str__(self) -> str:
        return str(self.value)
