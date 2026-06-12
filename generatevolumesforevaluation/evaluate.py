"""
evaluate.py
===========
Reads generated .npy designs and evaluates each against guidelines:

  1. Min channel width (horizontal scanline) >= 1.5mm  → PASS/FAIL
  2. Mean wall thickness (EDT) >= 0.5mm                → PASS/FAIL
Output:
    evaluation/results.csv     — full metrics + pass/fail per design
    evaluation/summary.png     — distribution plots + pass/fail breakdown
    evaluation/passed/         — symlinks/copies of passing design npys
"""

import argparse, os, csv, glob
import numpy as np
from scipy.ndimage import distance_transform_edt
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir',  type=str, default='./designs/npy')
parser.add_argument('--output_dir', type=str, default='./evaluation')
parser.add_argument('--canvas_mm',  type=float, default=15.0)
args = parser.parse_args()

MM_PER_PX      = args.canvas_mm / 384.0
MIN_CH_MM      = 1.5
MIN_WALL_MM    = 0.5

os.makedirs(args.output_dir, exist_ok=True)
os.makedirs(os.path.join(args.output_dir, 'passed'), exist_ok=True)

def min_horizontal_channel_mm(img):
    """Min horizontal void run width across all rows."""
    runs = []
    for row in range(img.shape[0]):
        line=img[row,:]; pad=np.concatenate([[1],line,[1]])
        t=np.diff(pad.astype(int))
        for s,e in zip(np.where(t==-1)[0], np.where(t==1)[0]):
            runs.append((e-s)*MM_PER_PX)
    arr = np.array(runs) if runs else np.array([0.])
    return float(arr.min()), float(arr.mean())

def mean_wall_thickness_mm(img):
    """Mean wall thickness via EDT on solid mask."""
    solid_mask = (img == 1).astype(np.float32)
    edt = distance_transform_edt(solid_mask)
    vals = edt[edt > 0]
    return float(2 * vals.mean()) * MM_PER_PX if len(vals) > 0 else 0.0

# Load and evaluate all designs
files = sorted(glob.glob(os.path.join(args.input_dir, 'design_*.npy')))
print(f"Found {len(files)} designs in {args.input_dir}\n")
print(f"{'Design':<14} {'Min ch (mm)':<14} {'Mean ch (mm)':<14} {'Mean wt (mm)':<14} {'ch pass':<10} {'wt pass':<10} {'OVERALL'}")
print("-"*90)

results = []
for fpath in files:
    img      = np.load(fpath)
    name     = os.path.splitext(os.path.basename(fpath))[0]
    min_ch, mean_ch = min_horizontal_channel_mm(img)
    mean_wt  = mean_wall_thickness_mm(img)
    porosity = float((img == 0).mean())

    pass_ch  = min_ch  >= MIN_CH_MM
    pass_wt  = mean_wt >= MIN_WALL_MM
    passes   = pass_ch and pass_wt

    results.append({'id': name, 'min_ch_mm': round(min_ch,3), 'mean_ch_mm': round(mean_ch,3),
                    'mean_wt_mm': round(mean_wt,3), 'porosity': round(porosity,3),
                    'pass_channel': pass_ch, 'pass_wall': pass_wt, 'passes': passes})

    print(f"{name:<14} {min_ch:<14.3f} {mean_ch:<14.3f} {mean_wt:<14.3f} "
          f"{'✓' if pass_ch else '✗':<10} {'✓' if pass_wt else '✗':<10} "
          f"{'PASS' if passes else 'FAIL'}")

    if passes:
        import shutil
        shutil.copy(fpath, os.path.join(args.output_dir, 'passed', os.path.basename(fpath)))

# Save CSV
with open(os.path.join(args.output_dir, 'results.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['id','min_ch_mm','mean_ch_mm','mean_wt_mm',
                                       'porosity','pass_channel','pass_wall','passes'])
    w.writeheader(); w.writerows(results)

# Summary stats
n        = len(results)
n_pass   = sum(r['passes'] for r in results)
n_fail   = n - n_pass
min_chs  = np.array([r['min_ch_mm']  for r in results])
mean_wts = np.array([r['mean_wt_mm'] for r in results])
porosities = np.array([r['porosity'] for r in results])

print(f"\n{'='*60}")
print(f"EVALUATION COMPLETE")
print(f"  Total:   {n}")
print(f"  Pass:    {n_pass} ({n_pass/n*100:.1f}%)")
print(f"  Fail:    {n_fail} ({n_fail/n*100:.1f}%)")
print(f"\n  Min channel width:   mean={min_chs.mean():.2f}  std={min_chs.std():.2f}  "
      f"range=[{min_chs.min():.2f}, {min_chs.max():.2f}] mm")
print(f"  Mean wall thickness: mean={mean_wts.mean():.2f}  std={mean_wts.std():.2f}  "
      f"range=[{mean_wts.min():.2f}, {mean_wts.max():.2f}] mm")
print(f"  Porosity:            mean={porosities.mean():.3f}  std={porosities.std():.3f}")
print(f"{'='*60}")

# Summary plot
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.patch.set_facecolor('white')
fig.suptitle(f'Evaluation results  |  {n} designs  |  {n_pass} pass ({n_pass/n*100:.0f}%)',
             fontsize=13, fontweight='bold')

# Min channel width distribution
axes[0].hist(min_chs, bins=30, color='#3498db', edgecolor='white', alpha=0.85)
axes[0].axvline(MIN_CH_MM, color='red', lw=2, linestyle='--', label=f'Threshold {MIN_CH_MM}mm')
axes[0].axvline(min_chs.mean(), color='black', lw=1.5, label=f'Mean={min_chs.mean():.2f}mm')
axes[0].set_xlabel('Min channel width (mm)'); axes[0].set_ylabel('Count')
axes[0].set_title('Min channel width distribution'); axes[0].legend(); axes[0].grid(True, alpha=0.3)

# Mean wall thickness distribution
axes[1].hist(mean_wts, bins=30, color='#e67e22', edgecolor='white', alpha=0.85)
axes[1].axvline(MIN_WALL_MM, color='red', lw=2, linestyle='--', label=f'Threshold {MIN_WALL_MM}mm')
axes[1].axvline(mean_wts.mean(), color='black', lw=1.5, label=f'Mean={mean_wts.mean():.2f}mm')
axes[1].set_xlabel('Mean wall thickness (mm)'); axes[1].set_ylabel('Count')
axes[1].set_title('Mean wall thickness distribution'); axes[1].legend(); axes[1].grid(True, alpha=0.3)

# Pass/fail breakdown
pass_both    = sum(1 for r in results if r['passes'])
fail_ch_only = sum(1 for r in results if not r['pass_channel'] and r['pass_wall'])
fail_wt_only = sum(1 for r in results if r['pass_channel'] and not r['pass_wall'])
fail_both_c  = sum(1 for r in results if not r['pass_channel'] and not r['pass_wall'])

cats   = ['Pass both', 'Fail ch only', 'Fail wt only', 'Fail both']
counts = [pass_both, fail_ch_only, fail_wt_only, fail_both_c]
colors = ['#2ecc71', '#e74c3c', '#e67e22', '#c0392b']
bars = axes[2].bar(cats, counts, color=colors, edgecolor='white', linewidth=1.5)
axes[2].set_ylabel('Count'); axes[2].set_title('Pass/Fail breakdown')
for bar, count in zip(bars, counts):
    axes[2].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                 str(count), ha='center', fontsize=10, fontweight='bold')
plt.setp(axes[2].xaxis.get_majorticklabels(), rotation=15, ha='right')

plt.tight_layout()
plt.savefig(os.path.join(args.output_dir, 'summary.png'),
            dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print(f"\nSummary plot → {args.output_dir}/summary.png")
print(f"Results CSV  → {args.output_dir}/results.csv")
print(f"Passed npy   → {args.output_dir}/passed/")
