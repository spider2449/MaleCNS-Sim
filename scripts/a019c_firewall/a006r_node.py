"""Exact A006R visible-run synthetic validation contract."""
from pathlib import Path
from a007c_node import ROOT, NODE, STATIC

ENTRY = Path(__file__).with_name('a006r_node.cjs').resolve()
SCRIPT = ROOT / 'tests/js/application_a006r.cjs'
PURPOSE = 'a006r-visible-run-contract-v1'


def command(purpose=PURPOSE):
    """Construct the exact script and individual source read grants."""
    from validation_firewall import check, SourceAccessDenied
    if purpose != PURPOSE:
        raise SourceAccessDenied('invalid A006R purpose')
    reads = [ENTRY, SCRIPT, *[STATIC / name for name in ('run-status.js', 'style.css', 'app.js')]]
    for path in reads:
        check(path)
        if path.resolve() != path or not path.is_file():
            raise SourceAccessDenied('noncanonical A006R input')
    return [str(NODE), '--permission', *['--allow-fs-read=' + str(path) for path in reads],
            str(ENTRY), purpose, str(STATIC)]


def admitted(argv, executable=None):
    """Match only the canonical A006R script, purpose, runtime and flags."""
    return (isinstance(argv, (list, tuple)) and len(argv) == 10
            and (executable is None or str(executable) == str(NODE))
            and list(argv) == command())
