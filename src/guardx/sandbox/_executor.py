import ast
import json
import os
import sys
from typing import cast

from pyseccomp import ALLOW, EQ, KILL, LOG, Arg, SyscallFilter

network_syscalls = [
    "socket",
    "socketpair",
    "setsockopt",
    "getsockopt",
    "getsockname",
    "getpeername",
    "bind",
    "listen",
    "accept",
    "accept4",
    "connect",
    "shutdown",
    "recvfrom",
    "recvmsg",
    "recvmmsg",
    "sendto",
    "sendmsg",
    "sendmmsg",
    "sethostname",
    "setdomainname",
]

# from CONFINE paper
critical_syscalls = [
    "clone",
    "execveat",
    "execve",
    "fork",
    "ptrace",
    "chmod",
    "mprotect",
    "setgid",
    "setreuid",
    "setuid",
    "accept4",
    "accept",
    "bind",
    "connect",
    "listen",
    "recvfrom",
    "socket",
]

cve_syscalls = [
    "set_thread_area",
    "mq_notify",
    "sched_getattr",
    "io_submit",
    "rt_sigqueueinfo",
    "rt_tgsigqueueinfo",
    "clock_nanosleep",
    "ioprio_get",
    "waitid",
    "inotify_init1",
    "semctl",
    "inotify_add_watch",
    "shmctl",
    "semget",
    "msgget",
    "shmget",
    "splice",
    "epoll_ctl",
    "setsockopt",
    "removexattr",
    "lremovexattr",
    "fremovexattr",
    "setxattr",
    "lsetxattr",
    "fsetxattr",
    "ioctl",
    "madvise",
    "execve",
    "execveat",
    "mremap",
    "epoll_pwait",
    "epoll_wait",
    "uselib",
]

crit_cves_syscalls = [
    "setuid",
    "epoll_ctl",
    "rt_tgsigqueueinfo",
    "execveat",
    "mprotect",
    "chmod",
    "setxattr",
    "rt_sigqueueinfo",
    "connect",
    "fsetxattr",
    "lsetxattr",
    "lremovexattr",
    "shmget",
    "uselib",
    "removexattr",
    "accept4",
    "fremovexattr",
    "setgid",
    "epoll_wait",
    "waitid",
    "semctl",
    "listen",
    "fork",
    "io_submit",
    "mremap",
    "msgget",
    "clone",
    "inotify_add_watch",
    "semget",
    "set_thread_area",
    "accept",
    "splice",
    "shmctl",
    "clock_nanosleep",
    "execve",
    "setsockopt",
    "socket",
    "madvise",
    "bind",
    "setreuid",
    "sched_getattr",
    "ioctl",
    "epoll_pwait",
    "recvfrom",
    "inotify_init1",
    "ioprio_get",
    "mq_notify",
    "ptrace",
]

network_syscalls = [
    "socket",
    "socketpair",
    "setsockopt",
    "getsockopt",
    "getsockname",
    "getpeername",
    "bind",
    "listen",
    "accept",
    "accept4",
    "connect",
    "shutdown",
    "recvfrom",
    "recvmsg",
    "recvmmsg",
    "sendto",
    "sendmsg",
    "sendmmsg",
    "sethostname",
    "setdomainname",
]


def _read_docker_default_seccomp():
    f = json.load(open("docker_seccomp_default.json"))
    syscalls = f['syscalls'][0]['names']
    return syscalls


def _memory_only_seccomp(filter):
    filter.add_rule(ALLOW, "rt_sigaction")
    filter.add_rule(ALLOW, "exit_group")
    filter.add_rule(ALLOW, "munmap")
    filter.add_rule(ALLOW, "read", Arg(0, EQ, sys.stdin.fileno()))
    filter.add_rule(ALLOW, "write", Arg(0, EQ, sys.stdout.fileno()))
    filter.add_rule(ALLOW, "write", Arg(0, EQ, sys.stderr.fileno()))


def _no_net_seccomp(filter):
    # for s in _read_docker_default_seccomp():
    #    if s not in network_syscalls:
    #        filter.add_rule(ALLOW, s)
    for s in network_syscalls:
        filter.add_rule(KILL, s)


def _no_crit_syscalls_seccomp(filter):
    # for s in _read_docker_default_seccomp():
    #    if s not in critical_syscalls:
    #        filter.add_rule(ALLOW, s)
    for s in critical_syscalls:
        filter.add_rule(KILL, s)


# def _docker_default(filter):
#    for s in _read_docker_default_seccomp():
#        filter.add_rule(ALLOW, s)


def setup_seccomp(category):
    if "unconfined" == category:
        return

    '''Arguments:
        defaction - the default filter action'''

    # default action
    f = SyscallFilter(defaction=KILL)

    # allow provided syscalls
    # with open(syscalls_allowed, 'r') as s:
    #    f.add_rule(ALLOW, s.read())

    # Category: Memory only execution
    if "memory" == category:
        f = SyscallFilter(defaction=KILL)
        _memory_only_seccomp(f)
    # Category: No network syscall access
    elif "nonet" == category:
        f = SyscallFilter(defaction=ALLOW)
        _no_net_seccomp(f)
    # Category: Disallow currated security sensitive syscalls
    elif "crit_syscalls" == category:
        f = SyscallFilter(defaction=ALLOW)
        _no_crit_syscalls_seccomp(f)
    elif "log" == category:
        f = SyscallFilter(defaction=LOG)

    # load the filter into the kernel
    f.load()


def unsafe_exec_python(python_code, globals_dict, locals_dict):
    parsed_statements = list(ast.iter_child_nodes(ast.parse(python_code)))
    if len(parsed_statements) > 1:
        exec(
            compile(
                ast.Module(body=cast(list[ast.stmt], parsed_statements[:-1]), type_ignores=[]),
                filename="<ast>",
                mode="exec",
            ),
            globals_dict,
            locals_dict,
        )
    last_statement = parsed_statements[-1]
    # Type guard: ensure last statement is an Expr node with a value attribute
    if isinstance(last_statement, ast.Expr):
        return (
            eval(
                compile(
                    ast.Expression(body=last_statement.value),
                    filename="<ast>",
                    mode="eval",
                ),
                globals_dict,
                locals_dict,
            ),
            globals_dict,
            locals_dict,
        )
    else:
        # If last statement is not an expression, return None
        return (None, globals_dict, locals_dict)


python_code = open("file.py", "r").read()

# Load globals from JSON file if it exists
globals_dict = {}
if os.path.exists("globals.json"):
    with open("globals.json", "r") as f:
        globals_dict = json.load(f)

# Always add __builtins__ to globals so exec can use built-in functions
# This is required for proper Python execution
if "__builtins__" not in globals_dict:
    globals_dict["__builtins__"] = __builtins__

setup_seccomp(sys.argv[1])
result, result_globals, result_locals = unsafe_exec_python(python_code, globals_dict, {})

# Try to serialize all of the locals. Exclude anything that isn't serializable.
serialized_stringified_locals = {}
for local in result_locals.keys():
    try:
        serialized_stringified_locals[local] = str(result_locals[local])
    except Exception:
        pass

print("-- THIS LINE IS METADATA --")  # noqa sic - leave a newline.
print(json.dumps({"locals": serialized_stringified_locals, "result": str(result)}))  # noqa
