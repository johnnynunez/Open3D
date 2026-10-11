"""Explicit test-harness overlay for invalid PEP 508 unary-not markers.
Never modifies the pinned source or its requirements file. Versions unchanged.
"""
from pathlib import Path
import hashlib
import json
from pip._vendor.packaging.requirements import Requirement, InvalidRequirement
p=Path('python/requirements_test.txt')
original=p.read_text(encoding='utf-8')
bad='not (sys_platform == "win32" and platform_machine == "ARM64")'
good='(sys_platform != "win32" or platform_machine != "ARM64")'
assert original.count(bad)==2
errors=[]
for line in original.splitlines():
    try: Requirement(line)
    except InvalidRequirement as e: errors.append(str(e))
assert len(errors)==2,errors
corrected=original.replace(bad,good)
requirements=[Requirement(line) for line in corrected.splitlines() if line]
truth=[]
for py in ['3.12','3.14']:
    for plat in ['win32','linux']:
        for arch in ['ARM64','AMD64']:
            env={'python_version':py,'sys_platform':plat,'platform_machine':arch}
            expected=(plat!='win32' or arch!='ARM64')
            assert requirements[5].marker.evaluate(env)==expected
            assert requirements[2].marker.evaluate(env)==(py<'3.14' and expected)
            truth.append({'env':env,'selected':[str(r) for r in requirements if r.marker is None or r.marker.evaluate(env)]})
out=Path('evidence');out.mkdir(exist_ok=True)
(out/'requirements_test.overlay.txt').write_text(corrected,encoding='utf-8')
(out/'requirements-overlay.json').write_text(json.dumps({'source_sha':'f47d260b2074d56d00e7a68eeabebd5bd45ad812','source_file':str(p),'original_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'replacement':{'from':bad,'to':good},'original_parser_errors':errors,'truth_table':truth,'scope':'test harness-only equivalent marker overlay, not unchanged original requirements acceptance'},indent=2),encoding='utf-8')
print('RED: original requirements fail PEP 508 parser twice; GREEN: equivalent overlay parses and eight environment cases verified.')
