"""
evaluate_3d.py
==============
Evaluates 3D volumes and identifies BEST vs WORST subsets.

Hard criteria (pass/fail):
  wall thickness >= 0.50mm
  solid fraction >= 0.08
  porosity       >= 0.85

Composite score (for ranking within pass/fail groups):
  Weighted by Pearson r from experimental results (§2.2.5):
    wall_thickness: r = +0.93  (t³ scaling, dominant predictor)
    solid_fraction: r = +0.76  (φ, secondary predictor)
    channel_width:  r = -0.50  (proxy, wider = better BNC infiltration)

  score = 0.93 * norm(wall_t) + 0.76 * norm(phi) + 0.50 * norm(mean_ch)

BEST:  pass_group, top score
WORST: fail_group, bottom score

Usage
-----
    python evaluate_3d.py \
        --vol_dir    ./volumes_3d \
        --output_dir ./eval_3d
"""

import argparse, os, csv, glob, json
import numpy as np
from scipy.ndimage import distance_transform_edt
from scipy.stats import mannwhitneyu
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('--vol_dir',    type=str,   default='./volumes_3d')
parser.add_argument('--output_dir', type=str,   default='./eval_3d')
parser.add_argument('--canvas_mm',  type=float, default=15.0)
parser.add_argument('--top_n',      type=int,   default=20)
args = parser.parse_args()

MM_PER_PX   = args.canvas_mm / 384.0
MIN_WALL_MM = 0.50
MIN_PHI     = 0.08
MIN_POR     = 0.85
os.makedirs(args.output_dir, exist_ok=True)

# Pearson weights from §2.2.5
W_WALL = 0.93
W_PHI  = 0.76

# ── Metrics ───────────────────────────────────────────────────────────────────
def mean_wall_thickness(vol):
    solid = (vol[::8] == 1).astype(np.float32)
    edt   = distance_transform_edt(solid)
    vals  = edt[edt > 0]
    return float(2 * vals.mean()) * MM_PER_PX if len(vals) > 0 else 0.0

def mean_channel_width(vol):
    runs = []
    for z in range(0, vol.shape[0], 8):
        layer = vol[z]
        for row in range(layer.shape[0]):
            line = layer[row,:]; pad = np.concatenate([[1],line,[1]])
            t = np.diff(pad.astype(int))
            for s,e in zip(np.where(t==-1)[0], np.where(t==1)[0]):
                runs.append((e-s)*MM_PER_PX)
    arr = np.array(runs) if runs else np.array([0.])
    return float(arr.mean())

# ── Evaluate ──────────────────────────────────────────────────────────────────
pass_files = sorted(glob.glob(os.path.join(args.vol_dir, 'pass', '*.npy')))
fail_files = sorted(glob.glob(os.path.join(args.vol_dir, 'fail', '*.npy')))
all_files  = pass_files + fail_files
print(f"Found {len(pass_files)} pass + {len(fail_files)} fail volumes\n")

results = []
for i, fpath in enumerate(all_files):
    name  = os.path.splitext(os.path.basename(fpath))[0]
    group = 'pass_group' if 'pass' in name else 'fail_group'
    vol   = np.load(fpath)
    print(f"[{i+1:03d}/{len(all_files)}] {name} ...", end=' ', flush=True)

    phi    = float(vol.mean())
    por    = 1.0 - phi
    wall   = mean_wall_thickness(vol)
    ch     = mean_channel_width(vol)

    p_wall = wall >= MIN_WALL_MM
    p_phi  = phi  >= MIN_PHI
    p_por  = por  >= MIN_POR
    passes = p_wall and p_phi

    results.append({
        'id':         name,
        'group':      group,
        'solid_frac': round(phi,  4),
        'porosity':   round(por,  4),
        'wall_t_mm':  round(wall, 3),
        'mean_ch_mm': round(ch,   3),
        'pass_wall':  p_wall,
        'pass_phi':   p_phi,
        'pass_por':   p_por,
        'passes_all': passes,
        'score':      0.0,   # filled below
    })
    print(f"phi={phi:.3f}({'✓' if p_phi else '✗'})  "
          f"wall={wall:.2f}mm({'✓' if p_wall else '✗'})  "
          f"{'PASS' if passes else 'FAIL'}")

# ── Normalise and compute composite score ────────────────────────────────────
walls = np.array([r['wall_t_mm']  for r in results])
phis  = np.array([r['solid_frac'] for r in results])
chs   = np.array([r['mean_ch_mm'] for r in results])

def norm(arr):
    rng = arr.max() - arr.min()
    return (arr - arr.min()) / rng if rng > 0 else np.zeros_like(arr)

scores = W_WALL * norm(walls) + W_PHI * norm(phis)
for r, s in zip(results, scores):
    r['score'] = round(float(s), 4)

# ── Save full results ─────────────────────────────────────────────────────────
fields = ['id','group','passes_all','score','solid_frac','porosity',
          'wall_t_mm','mean_ch_mm','pass_wall','pass_phi','pass_por']
with open(os.path.join(args.output_dir, 'results.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in results: w.writerow({k: r[k] for k in fields})

# ── BEST: top N from pass_group ───────────────────────────────────────────────
pass_r = [r for r in results if r['group']=='pass_group' and r['passes_all']]
fail_r = [r for r in results if r['group']=='fail_group' and not r['passes_all']]

# Fallback
if len(pass_r) == 0: pass_r = [r for r in results if r['group']=='pass_group']
if len(fail_r) == 0: fail_r = [r for r in results if r['group']=='fail_group']

best  = sorted(pass_r, key=lambda x: x['score'], reverse=True)[:args.top_n]
worst = sorted(fail_r, key=lambda x: x['score'])[:args.top_n]

for name, subset in [('best', best), ('worst', worst)]:
    with open(os.path.join(args.output_dir, f'{name}_subset.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in subset: w.writerow({k: r[k] for k in fields})

# ── Statistics ────────────────────────────────────────────────────────────────
metrics = ['solid_frac','porosity','wall_t_mm']
labels  = ['Solid fraction φ','Porosity','Wall thickness (mm)']
thresholds = [MIN_PHI, MIN_POR, MIN_WALL_MM]

stat_rows = []
print(f"\n{'='*70}")
print(f"BEST (n={len(best)}) vs WORST (n={len(worst)})")
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
    stat_rows.append({'metric':label,'key':key,
                      'best_mean':round(float(b.mean()),4),'best_std':round(float(b.std()),4),
                      'worst_mean':round(float(w.mean()),4),'worst_std':round(float(w.std()),4),
                      'p_value':round(float(pval),6) if not np.isnan(pval) else 'nan',
                      'significant':sig,'threshold':thr,
                      'pearson_weight': W_WALL if 'wall' in key else
                                        W_PHI  if 'frac' in key else None})

with open(os.path.join(args.output_dir, 'statistics.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=stat_rows[0].keys())
    w.writeheader(); w.writerows(stat_rows)

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.patch.set_facecolor('white')
fig.suptitle(f'BEST (n={len(best)}) vs WORST (n={len(worst)})\n'
             f'Score weighted by Pearson r: wall×0.93 + φ×0.76',
             fontsize=12, fontweight='bold')

for ax, key, label, thr, sr in zip(axes.flat, metrics, labels, thresholds, stat_rows):
    b_vals = [r[key] for r in best]
    w_vals = [r[key] for r in worst]
    ax.hist(b_vals, bins=15, alpha=0.7, color='#2ecc71',
            edgecolor='white', label=f'BEST (n={len(best)})')
    ax.hist(w_vals, bins=15, alpha=0.7, color='#e74c3c',
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
print(f"  results.csv      — all 100 volumes")
print(f"  best_subset.csv  — top {len(best)} by score")
print(f"  worst_subset.csv — bottom {len(worst)} by score")
print(f"  statistics.csv   — mean±std + p-values + Pearson weights")
print(f"  comparison.png   — distribution plots")