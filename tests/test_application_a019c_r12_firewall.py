"""Exact A014 direct-control admission negative controls."""
from pathlib import Path
import subprocess
import sys

import pytest
import validation_firewall as guard


def test_exact_direct_control_identity():
    command = [str(Path(sys._base_executable).resolve()), '-S', guard.DIRECT_ENTRY, guard.DIRECT_PURPOSE]
    assert guard.guarded_command(command) == command
    assert guard.mandatory_child(subprocess.list2cmdline(command), command[0])


@pytest.mark.parametrize('change', ['purpose', 'executable', 'shell', 'code', 'extra'])
def test_direct_control_rejects_alternatives(change):
    command = [str(Path(sys._base_executable).resolve()), '-S', guard.DIRECT_ENTRY, guard.DIRECT_PURPOSE]
    if change == 'purpose':
        command[-1] = 'unrecognized-purpose'
    elif change == 'executable':
        command[0] = str(Path(guard.ROOT) / 'alternate.exe')
    elif change == 'shell':
        command = ['cmd.exe', '/c', *command]
    elif change == 'code':
        command = [command[0], '-c', 'print(19)']
    else:
        command.append('unrecognized-argument')
    assert not guard.mandatory_child(subprocess.list2cmdline(command), command[0])
    with pytest.raises(guard.SourceAccessDenied):
        subprocess.Popen(command)


def test_shell_flag_rejected():
    command = [str(Path(sys._base_executable).resolve()), '-S', guard.DIRECT_ENTRY, guard.DIRECT_PURPOSE]
    with pytest.raises(guard.SourceAccessDenied):
        subprocess.Popen(command, shell=True)
