"""Exact browser-session regression permission contract."""
from pathlib import Path
from a007c_node import ROOT, NODE, STATIC

ENTRY = Path(__file__).with_name('session_node.cjs').resolve()
SCRIPT = ROOT / 'tests/js/workbench_session.cjs'
PURPOSE = 'browser-session-recovery-contract-v1'


def command():
    from validation_firewall import check, SourceAccessDenied
    reads = [ENTRY, SCRIPT, STATIC / 'app.js']
    for path in reads:
        check(path)
        if path.resolve() != path or not path.is_file():
            raise SourceAccessDenied('noncanonical browser-session input')
    return [str(NODE), '--permission',
            *['--allow-fs-read=' + str(path) for path in reads],
            str(ENTRY), PURPOSE, str(STATIC / 'app.js')]


def admitted(argv, executable=None):
    return (isinstance(argv, (list, tuple)) and len(argv) == 8
            and (executable is None or str(executable) == str(NODE))
            and list(argv) == command())
