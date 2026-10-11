"""Installed unchanged-wheel differential of the C++ ICPColored fixture.
Diagnostic variants do not replace or relax the original test.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import struct
import sys
import sysconfig
import traceback
import numpy as np
import open3d as o3d

out = Path('evidence'); out.mkdir(exist_ok=True)
assert sys.version_info[:2] == (3, 12)
assert sysconfig.get_platform() == 'win-arm64'
assert importlib.util.find_spec('torch') is None
assert not o3d._build_config['BUILD_PYTORCH_OPS']
assert o3d.__version__ == '0.20.0+f47d260'
exe = Path(sys.executable).read_bytes()
assert struct.unpack_from('<H', exe, struct.unpack_from('<I', exe, 60)[0]+4)[0] == 0xaa64
report = {'python':sys.version, 'platform':platform.platform(), 'executable':sys.executable,
          'open3d_file':o3d.__file__, 'build_config':o3d._build_config,
          'environment':{k:os.environ.get(k) for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','TBB_NUM_THREADS']},
          'scope':'Python binding reproduction, not rerun of missing tests.exe', 'cases':[]}
o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Debug)
data = o3d.data.DemoICPPointClouds()
report['data'] = [{'path':p, 'sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()} for p in data.paths]
init = o3d.core.Tensor([[.862,.011,-.507,.5],[-.139,.967,-.215,.7],[.487,.255,.835,-1.4],[0,0,0,1]], o3d.core.float64)
treg = o3d.t.pipelines.registration
lreg = o3d.pipelines.registration


def fixture(dtype):
    clouds = []
    for path in data.paths[:2]:
        p = o3d.t.io.read_point_cloud(path).voxel_down_sample(.05)
        for key in list(p.point):
            attr = p.point[key]
            p.point[key] = attr.to(dtype) / 255.0 if key == 'colors' and attr.dtype == o3d.core.uint8 else attr.to(dtype)
        clouds.append(p)
    return clouds


def stats(a):
    return {'shape':list(a.shape), 'finite':int(np.isfinite(a).sum()), 'size':int(a.size),
            'min':float(np.nanmin(a)), 'max':float(np.nanmax(a)), 'norm':float(np.linalg.norm(a))}


for repeat in range(2):
    for dtype in (o3d.core.float32, o3d.core.float64):
        source, target = fixture(dtype)
        row = {'repeat':repeat, 'dtype':str(dtype), 'variants':{}}
        # Legacy snapshots are taken before tensor ICP, matching C++ source.
        sl, tl = source.to_legacy(), target.to_legacy()
        try:
            res = treg.icp(source, target, .7, init, treg.TransformationEstimationForColoredICP(),
                           treg.ICPConvergenceCriteria(1e-6,1e-6,2), -1.)
            row['tensor'] = {'fitness':res.fitness,'rmse':res.inlier_rmse,'transformation':res.transformation.numpy().tolist()}
        except Exception as e:
            row['tensor_error'] = str(e)
        try:
            res = lreg.registration_colored_icp(sl,tl,.7,init.numpy(),lreg.TransformationEstimationForColoredICP(),lreg.ICPConvergenceCriteria(1e-6,1e-6,2))
            row['legacy'] = {'fitness':res.fitness,'rmse':res.inlier_rmse}
            if 'tensor' in row:
                row['original_oracles_pass'] = abs(row['tensor']['fitness']-res.fitness)<=.05 and abs(row['tensor']['rmse']-res.inlier_rmse)<=.02
        except Exception as e:
            row['legacy_error'] = str(e)
        # Explicitly compute identical automatic gradient settings for diagnostics.
        if 'color_gradients' not in target.point:
            target.estimate_color_gradients(max_nn=30, radius=1.4)
        grad = target.point.color_gradients.numpy()
        row['gradient_stats'] = stats(grad)
        np.savez_compressed(out / ('fixture-%s-%d.npz' % (str(dtype),repeat)),
                            source=source.point.positions.numpy(), target=target.point.positions.numpy(),
                            source_colors=source.point.colors.numpy(), target_colors=target.point.colors.numpy(),
                            normals=target.point.normals.numpy(), gradients=grad)
        if 'tensor_error' in row:
            # One-variable diagnostics: zero photometric gradient, or float32
            # gradient computation on the same target ordering then cast back.
            for mode in ('zero_gradient','float32_gradient'):
                alt=target.clone()
                if mode == 'zero_gradient':
                    alt.point.color_gradients=o3d.core.Tensor.zeros(grad.shape,dtype)
                else:
                    f=target.to(o3d.core.float32)
                    del f.point['color_gradients']
                    f.estimate_color_gradients(max_nn=30,radius=1.4)
                    alt.point.color_gradients=f.point.color_gradients.to(dtype)
                try:
                    res=treg.icp(source,alt,.7,init,treg.TransformationEstimationForColoredICP(),treg.ICPConvergenceCriteria(1e-6,1e-6,2),-1.)
                    row['variants'][mode]={'fitness':res.fitness,'rmse':res.inlier_rmse, 'diagnostic_only':True}
                except Exception as e:
                    row['variants'][mode]={'error':str(e),'diagnostic_only':True}
        report['cases'].append(row)
        (out/'probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print('PROBE_CASE',json.dumps(row),flush=True)
assert all(r.get('original_oracles_pass',False) for r in report['cases']), 'Unchanged fixture failed; see probe.json; diagnostic variants are not acceptance'
