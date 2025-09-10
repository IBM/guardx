"""Capability mapping."""

from enum import Enum

from guardx.analysis.specialization.x86_64_tables import Syscall


class Capability(str, Enum):
    """Enumeration for system capabilities."""

    MEMORY = "memory"
    FILESYSTEM = "filesystem"
    NETWORK = "network"
    IPC = "ipc"
    BPF = "bpf"
    INTROSPECTION = "introspection"

    def __str__(self) -> str:
        return str(self.value)


SC_CAPABILITIES_MAP = {
    Syscall.BRK: {Capability.MEMORY},
    Syscall.MMAP: {Capability.MEMORY},
    Syscall.MUNMAP: {Capability.MEMORY},
    Syscall.OPEN: {Capability.FILESYSTEM},
    # Syscall.READ: {Capability.FILESYSTEM},
    # Syscall.WRITE: {Capability.FILESYSTEM},
    Syscall.CLOSE: {Capability.FILESYSTEM},
    # TBD: complete mappings
}


def map_sc_capabilities(sc: Syscall) -> {}:
    if sc in SC_CAPABILITIES_MAP:
        return SC_CAPABILITIES_MAP[sc]
    return {}
