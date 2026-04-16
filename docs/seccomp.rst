## Seccomp policy category

The process (Python) running the AI code inside the container is further constrained with seccomp.

Set the seccomp policy category in `resources/config.yaml`.
Categories description below:

- memory: only allow rt\_sigaction, exit\_group, munmap, read stdin, write stdout, write stderr
- nonet: disallow network related syscalls
- crit\_syscalls: disallow syscalls associated with known CVEs or used as launchpad to carry out attacks.
- strict: allows read(), write(), _exit(), and sigreturn()
- log: logs all syscalls to auditd.log
- unconfined: no seccomp

