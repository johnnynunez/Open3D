"""Candidate numerical fix in a separate copy; foreign source never modified."""
from pathlib import Path
import difflib
import json
import math
import struct
import sys
src=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
f='cpp/open3d/core/linalg/kernel/SVD3x3.h'
original=(src/f).read_text(encoding='utf-8')
old='''template <typename scalar_t>
union un {
    scalar_t f;
    unsigned int ui;
};'''
new=old+'''

// Double bit selections require the entire IEEE-754 representation.
template <>
union un<double> {
    double f;
    unsigned long long ui;
};'''
assert original.count(old)==1
patched=original.replace(old,new)
a=patched.index('template <>\nOPEN3D_DEVICE OPEN3D_FORCE_INLINE void svd3x3<double>')
z=patched.index('template <>\nOPEN3D_DEVICE OPEN3D_FORCE_INLINE void svd3x3<float>')
part=patched[a:z]
def bits(v): return hex(struct.unpack('<Q',struct.pack('<d',v))[0])+'ULL'
constants={'0xffffffff':'0xffffffffffffffffULL','gone':bits(1.0),'gsine_pi_over_eight':bits(math.sin(math.pi/8)),'gcosine_pi_over_eight':bits(math.cos(math.pi/8))}
for old,new in constants.items(): part=part.replace(old,new)
patched=patched[:a]+part+patched[z:]
target=out/f;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(patched,encoding='utf-8')
# Matrix unchanged, needed by extraction only.
m=out/'cpp/open3d/core/linalg/kernel/Matrix.h';m.write_bytes((src/'cpp/open3d/core/linalg/kernel/Matrix.h').read_bytes())
(out/'svd-double-width.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),patched.splitlines(True),fromfile='a/'+f,tofile='b/'+f)))
(out/'constants.json').write_text(json.dumps(constants,indent=2))
print(constants)
