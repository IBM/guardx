"""Library schemas."""
from typing import Optional

from pydantic import BaseModel


class Logging(BaseModel):
    """The log configuration."""

    level: str


class Analysis(BaseModel):
    """Configurations for analysis."""

    sensitivity: str


class Execution(BaseModel):
    """The log configuration."""

    docker_image: Optional[str] = None
    policy_seccomp: str


class Config(BaseModel):
    """The main SDK configuration object."""

    logging: Optional[Logging] = Logging(level="DEBUG")
    analysis: Optional[Analysis] = None
    execution: Optional[Execution] = None
