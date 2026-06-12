"""
merge_and_evaluate.py
=====================
Merges two volumes directories into one combined set of 200 volumes,
then runs evaluation.

Usage
-----
    python merge_and_evaluate.py \
        --dir1       ./volumes_3d_v4 \
        --dir2       ./volumes_3d_v4old \
        --output_dir ./eval_3d_combined
"""

import argparse, os, csv, glob, shutil
import numpy as np
from scipy.ndimage import distance_transform_edt
from scipy.stats import mannwhitneyu
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('--dir1',       type=str, default='./volumes_3d_v4')
parser.add_argument('--dir2',       type=str, default='./volumes_3d_v4old')
parser.add_argument('--output_dir', type=str, default='./eval_3d_combined')
parser.add_argument('--canvas_mm',  type=float, default=15.0)
parser.add_argument('--top_n',      type=int,   default=20)
args = parser.parse_args()

MM_PER_PX   = args.canvas_mm / 384.0
MIN_WALL_MM = 0.50
MIN_PHI     = 0.08
MIN_POR     = 0.85
W_WALL      = 0.93
W_PHI       = 0.76
os.makedirs(args.output_dir, exist_ok=True)

# ── Collect all volume files from both dirs ───────────────────────────────────
def collect_files(base_dir):
    files = []
    for group in ['pass', 'fail']:
        pattern = os.path.join(base_dir, group, '*.npy')
        for f in sorted(glob.glob(pattern)):
            files.append((f, group))
    return files

files1 = collect_files(args.dir1)
files2 = collect_files(args.dir2)
all_files = files1 + files2
print(f"Dir1: {len(files1)} volumes")
print(f"Dir2: {len(files2)} volumes")
print(f"Total: {len(all_files)} volumes\n")

# ── Metrics ───────────────────────────────────────────────────────────────────
def mean_wall_thickness(vol):
    solid = (vol[::8] == 1).astype(np.float32)
    edt   = distance_transform_edt(solid)
    vals  = edt[edt > 0]
    return float(2 * vals.mean()) * MM_PER_PX if len(vals) > 0 else 0.0

# ── Evaluate ──────────────────────────────────────────────────────────────────
results = []
for i, (fpath, group) in enumerate(all_files):
    # Rename to avoid conflicts: prepend dir source
    src    = 'v4' if fpath.startswith(os.path.abspath(args.dir1)) else 'old'
    bname  = os.path.splitext(os.path.basename(fpath))[0]
    name   = f"{src}_{bname}"

    vol    = np.load(fpath)
    print(f"[{i+1:03d}/{len(all_files)}] {name} ...", end=' ', flush=True)

    phi    = float(vol.mean())
    por    = 1.0 - phi
    wall   = mean_wall_thickness(vol)

    p_wall = wall >= MIN_WALL_MM
    p_phi  = phi  >= MIN_PHI
    passes = p_wall and p_phi

    results.append({
        'id':         name,
        'group':      group,
        'source':     src,
        'solid_frac': round(phi,  4),
        'porosity':   round(por,  4),
        'wall_t_mm':  round(wall, 3),
        'pass_wall':  p_wall,
        'pass_phi':   p_phi,
        'passes_all': passes,
        'score':      0.0,
    })
    print(f"phi={phi:.3f}({'✓' if p_phi else '✗'})  "
          f"wall={wall:.2f}mm({'✓' if p_wall else '✗'})  "
          f"{'PASS' if passes else 'FAIL'}")

# ── Composite score ───────────────────────────────────────────────────────────
walls = np.array([r['wall_t_mm']  for r in results])
phis  = np.array([r['solid_frac'] for r in results])

def norm(arr):
    rng = arr.max() - arr.min()
    return (arr - arr.min()) / rng if rng > 0 else np.zeros_like(arr)

scores = W_WALL * norm(walls) + W_PHI * norm(phis)
for r, s in zip(results, scores):
    r['score'] = round(float(s), 4)

# ── Save results ──────────────────────────────────────────────────────────────
fields = ['id','group','source','passes_all','score',
          'solid_frac','porosity','wall_t_mm','pass_wall','pass_phi']
with open(os.path.join(args.output_dir, 'results.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in results: w.writerow({k: r[k] for k in fields})

# ── BEST and WORST subsets ────────────────────────────────────────────────────
pass_r = [r for r in results if r['group']=='pass' and r['passes_all']]
fail_r = [r for r in results if r['group']=='fail' and not r['passes_all']]

if len(pass_r) == 0: pass_r = [r for r in results if r['group']=='pass']
if len(fail_r) == 0: fail_r = [r for r in results if r['group']=='fail']

best  = sorted(pass_r, key=lambda x: x['score'], reverse=True)[:args.top_n]
worst = sorted(fail_r, key=lambda x: x['score'])[:args.top_n]

for name, subset in [('best', best), ('worst', worst)]:
    with open(os.path.join(args.output_dir, f'{name}_subset.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in subset: w.writerow({k: r[k] for k in fields})

# ── Statistics ────────────────────────────────────────────────────────────────
metrics    = ['solid_frac', 'porosity', 'wall_t_mm']
labels     = ['Solid fraction φ', 'Porosity', 'Wall thickness (mm)']
thresholds = [MIN_PHI, MIN_POR, MIN_WALL_MM]

stat_rows = []
print(f"\n{'='*70}")
print(f"Total: {len(results)}  |  BEST: {len(best)}  |  WORST: {len(worst)}")
print(f"{'Metric':<22} {'BEST mean±std':<24} {'WORST mean±std':<24} {'p':>8} sig")
print("-"*82)

for key, label, thr in zip(metrics, labels, thresholds):
    b = np.array([r[key] for r in best])
    w = np.array([r[key] for r in worst])
    _, pval = mannwhitneyu(b, w, alternative='two-sided') \
              if len(b)>1 and len(w)>1 else (None, float('nan'))
    sig = '***' if pval<0.001 else ('**' if pval<0.01 else ('*' if pval<0.05 else 'ns'))
    print(f"{label:<22} {b.mean():.3f}±{b.std():.3f}           "
          f"{w.mean():.3f}±{w.std():.3f}           {pval:>8.4f} {sig}")
    stat_rows.append({'metric':label, 'key':key,
                      'best_mean':round(float(b.mean()),4),
                      'best_std': round(float(b.std()), 4),
                      'worst_mean':round(float(w.mean()),4),
                      'worst_std': round(float(w.std()), 4),
                      'p_value':   round(float(pval),6) if not np.isnan(pval) else 'nan',
                      'significant': sig, 'threshold': thr})

with open(os.path.join(args.output_dir, 'statistics.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=stat_rows[0].keys())
    w.writeheader(); w.writerows(stat_rows)

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.patch.set_facecolor('white')
fig.suptitle(f'BEST (n={len(best)}) vs WORST (n={len(worst)}) — Combined {len(results)} volumes\n'
             f'Score: wall×0.93 + φ×0.76',
             fontsize=12, fontweight='bold')

for ax, key, label, thr, sr in zip(axes, metrics, labels, thresholds, stat_rows):
    ax.hist([r[key] for r in best],  bins=15, alpha=0.7, color='#2ecc71',
            edgecolor='white', label=f'BEST (n={len(best)})')
    ax.hist([r[key] for r in worst], bins=15, alpha=0.7, color='#e74c3c',
            edgecolor='white', label=f'WORST (n={len(worst)})')
    if thr is not None:
        ax.axvline(thr, color='black', lw=2, linestyle='--', label=f'Threshold {thr}')
    ax.text(0.97, 0.95, f"p={sr['p_value']}  {sr['significant']}",
            transform=ax.transAxes, ha='right', va='top', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.85))
    ax.set_xlabel(label); ax.set_ylabel('Count')
    ax.set_title(label); ax.legend(fontsize=8); ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(args.output_dir, 'comparison.png'),
            dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print(f"\nOutputs → {args.output_dir}/")
print(f"  results.csv      — all {len(results)} volumes")
print(f"  best_subset.csv  — top {len(best)} by score")
print(f"  worst_subset.csv — bottom {len(worst)} by score")
print(f"  statistics.csv   — mean±std + p-values")
print(f"  comparison.png")