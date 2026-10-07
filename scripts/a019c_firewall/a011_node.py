"""Exact validation-only A011 Node permission contract."""
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
NODE = Path('C:/Program Files/nodejs/node.exe').resolve()
ENTRY = Path(__file__).with_name('a011_node.cjs').resolve()
SCRIPT = ROOT / 'tests/js/application_a011.cjs'
STATIC = ROOT / 'src/malecns_sim/application/static'
PURPOSE = 'a011-synthetic-arena-dom-contract-v1'


def command(data, purpose=PURPOSE):
    """Grant reads only to the fixed synthetic fixture and unchanged JS assets."""
    from validation_firewall import check, SourceAccessDenied
    data = Path(data)
    check(data)
    if (str(data) != str(data.resolve()) or data.name != 'arena.json'
            or not data.is_relative_to(Path(tempfile.gettempdir()).resolve())
            or not data.is_file() or purpose != PURPOSE):
        raise SourceAccessDenied('invalid A011 synthetic fixture or purpose')
    reads = [ENTRY, SCRIPT, data, STATIC / 'arena.js']
    for path in reads:
        check(path)
        if path.resolve() != path or not path.is_file():
            raise SourceAccessDenied('noncanonical A011 input')
    return [str(NODE), '--permission',
            *['--allow-fs-read=' + str(path) for path in reads],
            str(ENTRY), purpose, str(data), str(STATIC)]


def admitted(argv, executable=None):
    """Deny alternate executable, flags, script, purpose and path spelling."""
    if not isinstance(argv, (list, tuple)) or len(argv) != 10:
        return False
    if executable is not None and str(executable) != str(NODE):
        return False
    try:
        return list(argv) == command(argv[-2], argv[-3])
    except (OSError, ValueError):
        return False


def environment():
    return {key: value for key, value in os.environ.items()
            if not key.upper().startswith('NODE_') and key.upper() != 'OPENSSL_CONF'}
