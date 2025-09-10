"""Define types for the analysis package."""
from enum import Enum
from typing import Dict, List

import docker


class PolicyType(str, Enum):
    """Enumeration of analysis types."""

    MEMORY = "memory"
    FILESYSTEM = "filesystem"
    NETWORK = "network"
    PERMISSIVE = "permissive"
    UNCONFINED = "unconfined"
    CRIT_SYSCALLS = "critical system calls"

    def __str__(self) -> str:
        return str(self.value)


class ExecutionResultKey(str, Enum):
    """Enumeration of execution result types."""

    EXIT_CODE = "exit_code"
    VIOLATIONS = "violations"

    def __str__(self) -> str:
        return str(self.value)


class ExecutionResults(Dict):
    """Execution summary dictionary."""

    def __init__(self, docker_exec_result: docker.models.containers.ExecResult):
        """Constructor.

        Initializes execution results.
        """
        # self.success = success
        # self.result = result
        # self.locals = locals
        # self.stdout = stdout
        self.docker_exec_result = docker_exec_result

    def get_exit_code(self) -> Dict:
        """Return the exist code from the execution."""
        return self[ExecutionResultKey.EXIT_CODE] if ExecutionResultKey.EXIT_CODE in self else None

    def get_violations(self) -> List[str]:
        """Return the set of policy violations detected in the program execution."""
        return self[ExecutionResultKey.VIOLATIONS] if ExecutionResultKey.VIOLATIONS in self else None

    def get_docker_result(self) -> docker.models.containers.ExecResult:
        """Return sandbox execution results."""
        return self.docker_exec_result
