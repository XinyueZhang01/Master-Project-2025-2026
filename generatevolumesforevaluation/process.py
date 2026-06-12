"""
process_npy.py
==============
Downsample + remove floating islands from npy volumes.

Usage:
    python process_npy.py \
        --vol_dir  "D:/BaiduNetdiskDownload/generatevolumes/volumes_3d_v4" \
        --output_dir "D:/BaiduNetdiskDownload/generatevolumes/processed_npy" \
        --downsample 8
"""
import argparse, os
import numpy as np
from scipy.ndimage import label

parser = argparse.ArgumentParser()
parser.add_argument('--vol_dir',    type=str, default='./volumes_3d_v4')
parser.add_argument('--output_dir', type=str, default='./processed_npy')
parser.add_argument('--downsample', type=int, default=8)
args = parser.parse_args()

MM_PER_PX = 15.0 / 384.0
os.makedirs(os.path.join(args.output_dir, 'pass'), exist_ok=True)
os.makedirs(os.path.join(args.output_dir, 'fail'), exist_ok=True)

best5 = [("pass","volume_pass_005"),("pass","volume_pass_023"),
         ("pass","volume_pass_050"),("pass","volume_pass_043"),
         ("pass","volume_pass_064")]
worst5 = [("fail","volume_fail_013"),("fail","volume_fail_003"),
          ("fail","volume_fail_020"),("fail","volume_fail_004"),
          ("fail","volume_fail_008")]

for group, name in best5 + worst5:
    npy_in  = os.path.join(args.vol_dir, group, f"{name}.npy")
    npy_out = os.path.join(args.output_dir, group, f"{name}_processed.npy")

    if not os.path.exists(npy_in):
        print(f"NOT FOUND: {npy_in}")
        continue

    vol = np.load(npy_in).astype(np.uint8)
    vol = vol[::args.downsample, ::args.downsample, ::args.downsample]

    labeled, n = label(vol)
    if n > 1:
        sizes = np.bincount(labeled.ravel())
        sizes[0] = 0
        vol = (labeled == sizes.argmax()).astype(np.uint8)

    np.save(npy_out, vol)
    voxel_mm = MM_PER_PX * args.downsample
    print(f"{name}: {vol.shape}  phi={vol.mean():.3f}  voxel={voxel_mm:.3f}mm  -> {npy_out}")

print("\nDone!")