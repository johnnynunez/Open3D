"""Extract unchanged numerical bodies, removing dependency includes only."""
from pathlib import Path
import hashlib
import json
import re
import sys
src=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
files=['cpp/open3d/core/linalg/kernel/Matrix.h','cpp/open3d/core/linalg/kernel/SVD3x3.h']
text='#include <algorithm>\n#include <cmath>\n#include <cstdio>\n#include <cstdint>\n#define OPEN3D_DEVICE\n#define OPEN3D_HOST_DEVICE\n#define OPEN3D_FORCE_INLINE inline\n'
for f in files:
    s=(src/f).read_text(encoding='utf-8')
    text+=re.sub(r'^#include.*$','',s,flags=re.M)
(out/'numeric.h').write_text(text,encoding='utf-8')
(out/'extraction.json').write_text(json.dumps({'files':{f:hashlib.sha256((src/f).read_bytes()).hexdigest() for f in files},'scope':'unchanged numerical bodies; removed includes; CPU macro definitions retained'},indent=2))
