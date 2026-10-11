"""Standalone wheel integrity/PE audit; not functional acceptance."""
import base64
import csv
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import zipfile


def audit(path):
    result = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    with zipfile.ZipFile(path) as z:
        names = [i.filename for i in z.infolist() if not i.is_dir()]
        assert len(names) == len(set(names)), 'duplicate ZIP names'
        record, = [n for n in names if n.endswith('.dist-info/RECORD')]
        rows = list(csv.reader(io.StringIO(z.read(record).decode())))
        assert len(rows) == len(names)
        assert set(r[0] for r in rows) == set(names)
        count = 0
        for n, h, size in rows:
            if n == record:
                assert not h and not size
                continue
            assert h and size, n
            alg, want = h.split('=', 1)
            data = z.read(n)
            assert base64.urlsafe_b64encode(hashlib.new(alg, data).digest()).rstrip(b'=').decode() == want, n
            assert len(data) == int(size), n
            count += 1
        native = {}
        for n in names:
            if not n.lower().endswith(('.pyd', '.dll', '.exe')):
                continue
            data = z.read(n)
            assert data[:2] == b'MZ', n
            pe = struct.unpack_from('<I', data, 60)[0]
            assert data[pe:pe+4] == b'PE\0\0', n
            native[n] = hex(struct.unpack_from('<H', data, pe+4)[0])
        result.update(record_verified=count, record_rows=len(rows), native=native,
                      metadata=z.read(next(n for n in names if n.endswith('.dist-info/METADATA'))).decode(),
                      wheel_metadata=z.read(next(n for n in names if n.endswith('.dist-info/WHEEL'))).decode(),
                      build_config=z.read('open3d/_build_config.py').decode())
        assert native and set(native.values()) == {'0xaa64'}, native
        assert 'Tag: cp312-cp312-win_arm64' in result['wheel_metadata']
        assert 'Version: 0.20.0+f47d260' in result['metadata']
    return result


if __name__ == '__main__':
    paths = [Path(p) for p in sys.argv[1:]]
    assert paths
    result = [audit(p) for p in paths]
    Path('wheel-audit-independent.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps([{k:v for k,v in row.items() if k not in ('metadata',)} for row in result], indent=2))
