"""Validation-only source firewall; never imported by production entrypoints."""
import functools
import json
import os
from pathlib import Path
import sys

ACTIVE = False
ROOT = Path(__file__).resolve().parents[2]
DENIED_ROOTS = [ROOT / "data"]
if os.environ.get("MALECNS_DATA_ROOT"):
    DENIED_ROOTS.append(Path(os.environ["MALECNS_DATA_ROOT"]).resolve())
LOG = os.environ.get("MALECNS_A019C_R2_LOG")
CHILD_ENTRY = str(Path(__file__).with_name('guarded_child.py').resolve())
DIRECT_ENTRY = str(Path(__file__).with_name('a014_direct_control.py').resolve())
DIRECT_PURPOSE = 'a014-tree-memory-control-v1'


def direct_control(command, executable=None):
    """Admit only the fixed base-interpreter synthetic memory control."""
    argv = audit_argv(command)
    expected = Path(sys._base_executable).resolve()
    return (argv == [str(expected), '-S', DIRECT_ENTRY, DIRECT_PURPOSE]
            and (executable is None or Path(executable).resolve() == expected))


def audit_argv(command):
    """Decode canonical Windows Popen serialization, rejecting ambiguity."""
    if isinstance(command, (list, tuple)):
        return list(command)
    if os.name != 'nt' or not isinstance(command, str) or not command:
        return []
    import ctypes
    from ctypes import wintypes
    import subprocess
    parser = ctypes.WinDLL('shell32').CommandLineToArgvW
    parser.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_int)]
    parser.restype = ctypes.POINTER(wintypes.LPWSTR)
    free = ctypes.WinDLL('kernel32').LocalFree
    free.argtypes = [ctypes.c_void_p]
    free.restype = ctypes.c_void_p
    count = ctypes.c_int()
    pointer = parser(command, ctypes.byref(count))
    if not pointer:
        return []
    try:
        argv = [pointer[i] for i in range(count.value)]
    finally:
        free(pointer)
    return argv if subprocess.list2cmdline(argv) == command else []


def mandatory_child(command, executable=None):
    """Match the executable and exact script position, never activation."""
    if direct_control(command, executable):
        return True
    argv = audit_argv(command)
    from a007c_node import admitted as a007c_admitted
    from a006r_node import admitted as a006r_admitted
    admitted = lambda argv, executable=None: a007c_admitted(argv, executable) or a006r_admitted(argv, executable)
    if admitted(argv, executable):
        return True
    if len(argv) < 3:
        return False
    expected = Path(sys.executable).resolve()
    if Path(argv[0]).resolve() != expected:
        return False
    if executable is not None and Path(executable).resolve() != expected:
        return False
    return argv[1] == CHILD_ENTRY and (
        argv[2] in ('-c', '-m') or not argv[2].startswith('-'))


def guarded_command(command):
    """Represent mandatory enforcement in argv, independent of environment."""
    from a007c_node import admitted as a007c_admitted
    from a006r_node import admitted as a006r_admitted
    admitted = lambda argv, executable=None: a007c_admitted(argv, executable) or a006r_admitted(argv, executable)
    if direct_control(command) or admitted(command):
        if os.environ.get('MALECNS_A019C_R2_FIREWALL') != '1':
            raise SourceAccessDenied('FIREWALL_REQUIRED_BUT_NOT_ACTIVE')
        return list(command)
    if not isinstance(command, (list, tuple)) or not command:
        raise SourceAccessDenied('A019 children require an explicit Python argv')
    if Path(command[0]).resolve() != Path(sys.executable).resolve():
        raise SourceAccessDenied('unsupported A019 child executable')
    if len(command) > 1 and str(command[1]) == CHILD_ENTRY:
        return list(command)
    if os.environ.get('MALECNS_A019C_R2_FIREWALL') != '1':
        raise SourceAccessDenied('FIREWALL_REQUIRED_BUT_NOT_ACTIVE')
    return [command[0], CHILD_ENTRY, *command[1:]]


class SourceAccessDenied(PermissionError):
    """Raised before a prohibited payload is passed to any reader."""


def category(path):
    name = str(path).lower()
    if "mapping" in name:
        return "REAL_MAPPING"
    if "provenance" in name:
        return "REAL_PROVENANCE"
    if "neurotransmitter" in name:
        return "REAL_NEUROTRANSMITTER"
    if "annotation" in name:
        return "REAL_ANNOTATION"
    if "connectome" in name or "weight" in name or "edge" in name:
        return "REAL_CONNECTIVITY"
    if "neuron" in name or "metadata" in name:
        return "REAL_NEURON_METADATA"
    return "REAL_OTHER_REGISTERED_DATA"


def record(kind, **details):
    if LOG:
        with open(LOG, "a", encoding="utf-8") as stream:
            stream.write(json.dumps(dict(kind=kind, pid=os.getpid(), **details)) + "\n")


def check(source):
    if isinstance(source, int) or not isinstance(source, (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(source)).resolve()
    name = str(path).lower()
    denied = any(path.is_relative_to(root.resolve()) for root in DENIED_ROOTS)
    # Registered release names remain denied if relocated outside data/.
    denied |= "male-cns-v1" in name or "male-cns/v1.0" in path.as_posix().lower()
    if denied:
        record("blocked", category=category(path), path=str(path), before_content_read=True)
        raise SourceAccessDenied(f"A019C-R2 registered source denied: {path}")


def wrap(module, name):
    original = getattr(module, name)
    @functools.wraps(original)
    def guarded(source, *args, **kwargs):
        check(source)
        return original(source, *args, **kwargs)
    setattr(module, name, guarded)


def install():
    global ACTIVE
    if ACTIVE:
        return
    def audit(event, args):
        if event == "open":
            check(args[0])
        if event == "subprocess.Popen":
            if not mandatory_child(args[1], args[0]):
                raise SourceAccessDenied('child lacks mandatory firewall entrypoint')
    sys.addaudithook(audit)
    import subprocess
    original_init = subprocess.Popen.__init__
    def child_init(self, args, *positional, **kwargs):
        if kwargs.get('shell'):
            raise SourceAccessDenied('shell children are outside the A019 contract')
        from a007c_node import admitted as a007c_admitted
        from a006r_node import admitted as a006r_admitted
        admitted = lambda argv: a007c_admitted(argv) or a006r_admitted(argv)
        if admitted(args):
            env = kwargs.get('env', os.environ)
            if (env.get('MALECNS_A019C_R2_FIREWALL') != '1'
                    or any(k.upper().startswith('NODE_') or k.upper() == 'OPENSSL_CONF' for k in env)
                    or kwargs.get('cwd') != str(ROOT)
                    or kwargs.get('executable') is not None
                    or kwargs.get('close_fds', True) is not True
                    or not ACTIVE):
                raise SourceAccessDenied('invalid A007C child activation/environment/cwd')
            record('trusted_node_admitted', argv=list(args), cwd=str(ROOT))
        return original_init(self, guarded_command(args), *positional, **kwargs)
    subprocess.Popen.__init__ = child_init
    # Arrow native opens do not reliably emit CPython's open audit event.
    import pyarrow
    import pyarrow.feather
    import pyarrow.parquet
    import pyarrow._feather
    # Intercept before the extension constructor can open an OS/native source.
    wrap(pyarrow._feather, "FeatherReader")
    for module, names in ((pyarrow, ("memory_map", "OSFile", "input_stream")),
                          (pyarrow.feather, ("read_table", "read_feather")),
                          (pyarrow.parquet, ("read_table", "read_schema", "ParquetFile"))):
        for name in names:
            wrap(module, name)
    ACTIVE = True
    record("active", denied_roots=[str(root) for root in DENIED_ROOTS])
