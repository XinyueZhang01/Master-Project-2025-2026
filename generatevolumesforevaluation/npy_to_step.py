import os
import numpy as np
from scipy.ndimage import label
import cadquery as cq

MM_PER_PX = 15.0 / 384.0

VOL_DIR = r"D:\BaiduNetdiskDownload\generatevolumes\volumes_3d_v4"
OUT_DIR = r"D:\BaiduNetdiskDownload\generatevolumes\step_files"
os.makedirs(OUT_DIR, exist_ok=True)

best5  = [("pass","volume_pass_005"),("pass","volume_pass_023"),
          ("pass","volume_pass_050"),("pass","volume_pass_043"),
          ("pass","volume_pass_064")]
worst5 = [("fail","volume_fail_013"),("fail","volume_fail_003"),
          ("fail","volume_fail_020"),("fail","volume_fail_004"),
          ("fail","volume_fail_008")]

def convert(npy_path, step_path, downsample=16):
    vol = np.load(npy_path).astype(np.uint8)
    vol = vol[::downsample, ::downsample, ::downsample]
    voxel_mm = MM_PER_PX * downsample
    print(f"  Shape: {vol.shape}  voxel={voxel_mm:.3f}mm")

    # Keep largest component
    labeled, n = label(vol)
    if n > 1:
        sizes = np.bincount(labeled.ravel())
        sizes[0] = 0
        vol = (labeled == sizes.argmax()).astype(np.uint8)
        print(f"  Removed {n-1} islands")

    # Build solid from voxels using cadquery
    # Each solid voxel = a box, union all boxes
    solid_positions = np.argwhere(vol == 1)
    print(f"  Building solid from {len(solid_positions)} voxels...")

    result = cq.Workplane("XY")
    boxes = []
    for pos in solid_positions:
        z, y, x = pos
        cx = (x + 0.5) * voxel_mm
        cy = (y + 0.5) * voxel_mm
        cz = (z + 0.5) * voxel_mm
        boxes.append(cq.Solid.makeBox(voxel_mm, voxel_mm, voxel_mm,
                                       cq.Vector(cx - voxel_mm/2,
                                                 cy - voxel_mm/2,
                                                 cz - voxel_mm/2)))

    print(f"  Unioning {len(boxes)} boxes...")
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
    from OCP.TopoDS import TopoDS_Shape

    # Union in batches
    combined = boxes[0].wrapped
    for i, box in enumerate(boxes[1:], 1):
        fuse = BRepAlgoAPI_Fuse(combined, box.wrapped)
        fuse.Build()
        combined = fuse.Shape()
        if i % 100 == 0:
            print(f"    {i}/{len(boxes)-1}...")

    # Export as STEP
    from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
    from OCP.IFSelect import IFSelect_RetDone
    writer = STEPControl_Writer()
    writer.Transfer(combined, STEPControl_AsIs)
    status = writer.Write(step_path)
    if status == IFSelect_RetDone:
        print(f"  STEP: {step_path} ({os.path.getsize(step_path)/1e6:.1f} MB)")
    else:
        print(f"  STEP write failed")

for subset, items in [("best", best5), ("worst", worst5)]:
    print(f"\n=== {subset.upper()} ===")
    for i, (group, name) in enumerate(items):
        npy_path  = os.path.join(VOL_DIR, group, f"{name}.npy")
        step_path = os.path.join(OUT_DIR, f"{subset}_{i+1:02d}_{name}.step")
        print(f"\n[{i+1}/5] {name}")
        if not os.path.exists(npy_path):
            print(f"  NOT FOUND: {npy_path}")
            continue
        try:
            convert(npy_path, step_path)
        except Exception as e:
            print(f"  ERROR: {e}")

print("\nDone!")