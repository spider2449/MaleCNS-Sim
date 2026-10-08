"""Certify the native synthetic symlink broker inside a fresh Windows capsule."""
from __future__ import annotations
import ctypes
from ctypes import wintypes as W
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]


def main():
    sys.path.insert(0, str(ROOT / 'scripts'))
    from a025_windows_isolation import launch, require, api
    from a025_metadata_controls import MetadataRights
    from a025_symlink_broker import SyntheticSymlinkBroker
    from a023_local_repro import Job
    root = Path('C:/TEMP') / ('malecns-a025-symlink-' + uuid.uuid4().hex)
    tools, source, output = root / 'tools', root / 'input', root / 'output'
    for path in (tools, source / 'tests', source / 'scripts', output / 'temp'):
        path.mkdir(parents=True)
    runtime = Path(sys._base_executable).parent
    for path in runtime.iterdir():
        if path.is_file() and (path.suffix.lower() == '.dll' or path.name == 'python.exe'):
            shutil.copy2(path, tools / path.name)
    for name in ('Lib', 'DLLs'):
        shutil.copytree(runtime / name, tools / name,
                       ignore=shutil.ignore_patterns('__pycache__', 'site-packages'))
    for name in ('a025_symlink_compat.py', 'a025_tempfile_compat.py', 'a023_fail_closed_inspect.py'):
        shutil.copy2(ROOT / 'scripts' / name, source / 'scripts' / name)
    shutil.copy2(ROOT / 'tests/test_a023_fail_closed_inspect.py', source / 'tests/test_a023_fail_closed_inspect.py')
    probe = source / 'probe.py'
    probe.write_text('''import sys,os,json,importlib.util,unittest
from pathlib import Path
out=Path(sys.argv[1]); sys.path.insert(0,str(Path(__file__).parent/'scripts'))
import a025_tempfile_compat,a025_symlink_compat
a025_tempfile_compat.install([out]); a025_symlink_compat.install()
os.environ['TEMP']=os.environ['TMP']=str(out/'temp')
import tempfile; tempfile.tempdir=str(out/'temp')
spec=importlib.util.spec_from_file_location('original_inspector_tests',Path(__file__).parent/'tests/test_a023_fail_closed_inspect.py')
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
suite=unittest.TestSuite([module.InspectorTests('test_symlink_escape')])
result=unittest.TextTestRunner(verbosity=2).run(suite)
assert result.testsRun==1 and not result.skipped and result.wasSuccessful()
(out/'probe.json').write_text(json.dumps({'status':'PASS','original_symlink_test':1,'skipped':0}))
''')
    user = ctypes.WinDLL('userenv'); adv = ctypes.WinDLL('advapi32'); kernel = api()
    user.CreateAppContainerProfile.argtypes = [W.LPCWSTR, W.LPCWSTR, W.LPCWSTR, ctypes.c_void_p, W.DWORD, ctypes.POINTER(ctypes.c_void_p)]
    user.DeleteAppContainerProfile.argtypes = [W.LPCWSTR]
    adv.ConvertSidToStringSidW.argtypes = [ctypes.c_void_p, ctypes.POINTER(W.LPWSTR)]
    adv.FreeSid.argtypes = [ctypes.c_void_p]; kernel.LocalFree.argtypes = [ctypes.c_void_p]
    sid, text = ctypes.c_void_p(), W.LPWSTR(); profile='MaleCNSA025.Link.'+uuid.uuid4().hex
    assert user.CreateAppContainerProfile(profile,profile,'Synthetic symlink control',None,0,ctypes.byref(sid))==0
    broker=job=metadata=None; loopback=False
    evidence={'status':'FAIL','run':str(root),'claim':'Synthetic native link control only',
              'control_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'original_source_hashes':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                  for name in ('scripts/a023_fail_closed_inspect.py','tests/test_a023_fail_closed_inspect.py')}}
    try:
        require(adv.ConvertSidToStringSidW(sid,ctypes.byref(text)))
        metadata=MetadataRights(sid,[Path('C:/'),Path('C:/TEMP'),root])
        for path, rights in ((tools,'(OI)(CI)RX'),(source,'(OI)(CI)RX'),(output,'(OI)(CI)M')):
            subprocess.run(['icacls',str(path),'/grant','*'+text.value+':'+rights],check=True,capture_output=True)
        subprocess.run(['icacls',str(output),'/setintegritylevel','(OI)(CI)L'],check=True,capture_output=True)
        subprocess.run(['CheckNetIsolation.exe','LoopbackExempt','-a','-n='+profile],check=True,capture_output=True); loopback=True
        broker=SyntheticSymlinkBroker(output/'temp'); job=Job()
        import urllib.request, urllib.error
        endpoint=broker.environment()
        negative=urllib.request.Request(endpoint['MALECNS_A025_SYMLINK_URL'],
            data=json.dumps({'target':str(ROOT/'data/outside.py'),
                             'link':str(output/'temp/tmp-negative/link.py')}).encode(),
            headers={'Authorization':endpoint['MALECNS_A025_SYMLINK_TOKEN']},method='POST')
        try:
            urllib.request.build_opener(urllib.request.ProxyHandler({})).open(negative,timeout=5)
        except urllib.error.HTTPError as error:
            assert error.code==403
            evidence['outside_request_denial']='PASS; rejected before filesystem metadata'
        else:
            raise RuntimeError('Outside synthetic broker request accepted')
        evidence['process']=launch(tools/'python.exe',probe,output,sid,job,internet=True,extra_environment=broker.environment())
        evidence['probe']=json.loads((output/'probe.json').read_text()) if (output/'probe.json').exists() else None
        evidence['receipts']=broker.receipts
        evidence['helpers']={name:hashlib.sha256((ROOT/'scripts'/name).read_bytes()).hexdigest() for name in ('a025_symlink_broker.py','a025_symlink_compat.py','a025_windows_isolation.py','a025_metadata_controls.py','a023_local_repro.py')}
        if evidence['process']['exit']==0 and evidence['process']['job']['active']==0 and len(broker.receipts)==1:
            evidence['status']='PASS'
    finally:
        if job: job.close(); evidence['job_cleanup']='closed'
        if broker: broker.close(); evidence['broker_cleanup']='closed'
        if loopback: subprocess.run(['CheckNetIsolation.exe','LoopbackExempt','-d','-n='+profile],check=True,capture_output=True)
        if metadata: metadata.close(); evidence['metadata_cleanup']='removed'
        evidence['profile_cleanup_hresult']=user.DeleteAppContainerProfile(profile)
        if text: kernel.LocalFree(text)
        adv.FreeSid(sid)
        (root/'symlink.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps({'status':evidence['status'],'evidence':str(root/'symlink.json')}))
    if evidence['status']!='PASS' or evidence['profile_cleanup_hresult']!=0: raise SystemExit(1)

if __name__=='__main__': main()
