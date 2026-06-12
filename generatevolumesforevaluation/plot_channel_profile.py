"""
Plot Min Channel Width Profile
================================
Loads the 200 scaffold designs and plots their horizontal
channel width distribution.

Usage:
    python plot_channel_profile.py --npy_dir ./final_200/npy --output_dir .

Requirements:
    pip install numpy matplotlib
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import csv, os

parser = argparse.ArgumentParser()
parser.add_argument('--npy_dir',    type=str, default='./final_200/npy')
parser.add_argument('--csv_path',   type=str, default='./designs_metrics.csv')
parser.add_argument('--output_dir', type=str, default='.')
parser.add_argument('--threshold',  type=float, default=1.5, help='Pass threshold in mm')
parser.add_argument('--canvas_mm',  type=float, default=15.0)
args = parser.parse_args()

MM_PER_PX = args.canvas_mm / 384.0

def get_min_channel(img):
    runs = []
    for row in range(img.shape[0]):
        line = img[row,:]
        pad  = np.concatenate([[1],line,[1]])
        t    = np.diff(pad.astype(int))
        for s,e in zip(np.where(t==-1)[0], np.where(t==1)[0]):
            runs.append((e-s)*MM_PER_PX)
    arr = np.array(runs) if runs else np.array([0.])
    return float(arr.min()), float(arr.mean())

# Load metrics from CSV if exists, else compute
if os.path.exists(args.csv_path):
    print(f"Loading metrics from {args.csv_path}")
    rows = list(csv.DictReader(open(args.csv_path)))
    mins  = np.array([float(r['min_ch_mm'])  for r in rows])
    means = np.array([float(r['mean_ch_mm']) for r in rows])
else:
    print(f"Computing metrics from {args.npy_dir}...")
    files = sorted([f for f in os.listdir(args.npy_dir) if f.endswith('.npy')])
    mins, means = [], []
    for i,f in enumerate(files):
        img = np.load(os.path.join(args.npy_dir, f))
        mn, me = get_min_channel(img)
        mins.append(mn); means.append(me)
        if (i+1)%50==0: print(f"  {i+1}/{len(files)}")
    mins  = np.array(mins)
    means = np.array(means)

passes = mins >= args.threshold
n      = len(mins)
n_pass = passes.sum()

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.patch.set_facecolor('white')
fig.suptitle(f'Min Channel Width Profile — {n} Designs', fontsize=15, fontweight='bold')

# Plot 1: sorted bar
sorted_idx  = np.argsort(mins)
sorted_mins = mins[sorted_idx]
colors      = ['#2ecc71' if passes[i] else '#e74c3c' for i in sorted_idx]
axes[0,0].bar(range(n), sorted_mins, color=colors, edgecolor='none', width=1.0)
axes[0,0].axhline(args.threshold, color='black', lw=2, linestyle='--')
axes[0,0].set_xlabel('Design rank (sorted)')
axes[0,0].set_ylabel('Min channel width (mm)')
axes[0,0].set_title(f'Sorted min channel width  |  {n_pass}/{n} pass (≥{args.threshold}mm)')
axes[0,0].legend(handles=[
    mpatches.Patch(color='#2ecc71', label=f'Pass: {n_pass}'),
    mpatches.Patch(color='#e74c3c', label=f'Fail: {n-n_pass}'),
    plt.Line2D([0],[0],color='black',linestyle='--',label=f'{args.threshold}mm threshold')
])
axes[0,0].grid(True, alpha=0.3, axis='y')

# Plot 2: histogram
axes[0,1].hist(mins, bins=40, color='#3498db', edgecolor='white', alpha=0.85)
axes[0,1].axvline(args.threshold,         color='red',    lw=2, linestyle='--',
                  label=f'Threshold {args.threshold}mm')
axes[0,1].axvline(mins.mean(),            color='black',  lw=2,
                  label=f'Mean={mins.mean():.2f}mm')
axes[0,1].axvline(np.percentile(mins,10), color='orange', lw=1.5, linestyle=':',
                  label=f'P10={np.percentile(mins,10):.2f}mm')
axes[0,1].axvline(np.percentile(mins,90), color='purple', lw=1.5, linestyle=':',
                  label=f'P90={np.percentile(mins,90):.2f}mm')
axes[0,1].set_xlabel('Min channel width (mm)')
axes[0,1].set_ylabel('Count')
axes[0,1].set_title('Distribution of min channel widths')
axes[0,1].legend(fontsize=8)
axes[0,1].grid(True, alpha=0.3)

# Plot 3: scatter min vs mean
axes[1,0].scatter(means[~passes], mins[~passes], c='#e74c3c', alpha=0.6,
                  s=25, label=f'Fail: {(~passes).sum()}')
axes[1,0].scatter(means[passes],  mins[passes],  c='#2ecc71', alpha=0.6,
                  s=25, label=f'Pass: {passes.sum()}')
axes[1,0].axhline(args.threshold, color='black', lw=1.5, linestyle='--',
                  label=f'{args.threshold}mm threshold')
axes[1,0].set_xlabel('Mean channel width (mm)')
axes[1,0].set_ylabel('Min channel width (mm)')
axes[1,0].set_title('Min vs Mean channel width')
axes[1,0].legend(fontsize=8)
axes[1,0].grid(True, alpha=0.3)

# Plot 4: generation order
axes[1,1].bar(range(1,n+1), mins,
              color=['#2ecc71' if p else '#e74c3c' for p in passes],
              edgecolor='none', width=1.0)
axes[1,1].axhline(args.threshold, color='black', lw=1.5, linestyle='--',
                  label=f'{args.threshold}mm threshold')
axes[1,1].set_xlabel('Design index')
axes[1,1].set_ylabel('Min channel width (mm)')
axes[1,1].set_title('Min channel width in generation order')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3, axis='y')

plt.tight_layout()
out = os.path.join(args.output_dir, 'min_channel_profile.png')
plt.savefig(out, dpi=200, bbox_inches='tight', facecolor='white')
print(f"\nPlot saved → {out}")
print(f"Mean={mins.mean():.3f}  Std={mins.std():.3f}  "
      f"Min={mins.min():.3f}  Max={mins.max():.3f}  Pass={n_pass}/{n}")
