import hashlib
import json
from pathlib import Path
import subprocess


def api(endpoint):
    return json.loads(subprocess.check_output(['gh','api',endpoint],text=True,encoding='utf-8'))


sha='f47d260b2074d56d00e7a68eeabebd5bd45ad812'
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==sha
run=api('repos/johnnynunez/Open3D/actions/runs/38180281801')
assert run['head_sha']=='ef205fd1e30393ad93a0d67e7fe3c5458c064612'
assert run['conclusion']=='failure', 'Parent failed C++ gate must remain recorded'
jobs=api('repos/johnnynunez/Open3D/actions/runs/38180281801/jobs')['jobs']
job,=[j for j in jobs if j['name']=='Build ARM64 (Release)']
steps={s['name']:s['conclusion'] for s in job['steps']}
for name in ['Build','Build Python wheel','Verify native Python, wheel PE payloads and RECORD']:
    assert steps[name]=='success', (name,steps[name])
assert steps['Run C++ unit tests']=='failure'
a=api('repos/johnnynunez/Open3D/actions/artifacts/11718448636')
assert a['workflow_run']['id']==38180281801 and not a['expired']
assert a['digest']=='sha256:15bfe6e3ef9e6c00a437c9b3d5fc84d757a879886550993f6bd60bfb019a0cd7'
result={'source_sha':sha,'parent_run':38180281801,'parent_ci_sha':run['head_sha'],'parent_conclusion':run['conclusion'],'build_steps':steps,'artifact':a,'functional_acceptance':False,'gate':'Successful build, packaging, PE/RECORD plus pinned retained digest permits independent wheel diagnostics; C++ failure is NOT waived.'}
Path('evidence/parent-provenance.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
