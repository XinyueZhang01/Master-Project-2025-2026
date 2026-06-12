"""
2D Scaffold Generator + Initial Screening
==========================================
Generates N 2D binary scaffold designs from a pre-trained VAE,
then screens each against two geometric guidelines:

  1. Minimum channel width  >= 1.5 mm  (void/black regions)
  2. Minimum wall thickness >= 0.5 mm  (solid/white regions)

Physical scale: 384 x 384 px = 15 mm x 15 mm
  → 1 px = 15/384 = 0.03906 mm
  → Min channel: 1.5 mm = 38.4 px
  → Min wall:    0.5 mm = 12.8 px

Screening method
----------------
Uses Euclidean Distance Transform (EDT) on binary masks.
EDT gives the distance from each foreground pixel to the nearest
background pixel. The minimum inscribed circle diameter at the
thinnest point = 2 × min(EDT). This is a standard morphological
measurement used in scaffold analysis (e.g. trabecular thickness
measurement in micro-CT, Hildebrand & Rüegsegger 1997,
doi:10.1046/j.1365-2818.1997.1340694.x).

Output
------
  output_dir/
    all/png/design_NNN.png       — all generated designs
    all/npy/design_NNN.npy       — all designs as numpy arrays
    passed/png/design_NNN.png    — designs that passed screening
    passed/npy/design_NNN.npy    — passed designs as numpy arrays
    screening_results.csv        — full metrics for every design
    summary.png                  — visual summary of pass/fail

Usage
-----
    python screen_and_generate.py --n 200 --output_dir ./screened_designs

Requirements
------------
    pip install torch torchvision scipy scikit-image numpy matplotlib
"""

import argparse, os, csv
import numpy as np
import torch
import torch.nn as nn
from scipy.ndimage import gaussian_filter, zoom, distance_transform_edt
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Args ────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument('--n',           type=int,   default=200)
parser.add_argument('--model_path',  type=str,   default='./model_weights')
parser.add_argument('--output_dir',  type=str,   default='./screened_designs')
parser.add_argument('--latent_size', type=int,   default=16)
parser.add_argument('--vf',          type=float, default=0.15)
parser.add_argument('--seed',        type=int,   default=42)
parser.add_argument('--canvas_mm',   type=float, default=15.0,
                    help='Physical size of the 384px canvas in mm')
args = parser.parse_args()

# ── Physical scale ──────────────────────────────────────────────────────────
IMG_PX       = 384
MM_PER_PX    = args.canvas_mm / IMG_PX          # 0.03906 mm/px

MIN_CHANNEL_MM  = 1.5
MIN_WALL_MM     = 0.5
MIN_CHANNEL_PX  = MIN_CHANNEL_MM / MM_PER_PX    # 38.4 px
MIN_WALL_PX     = MIN_WALL_MM    / MM_PER_PX    # 12.8 px

print(f"Scale:          {MM_PER_PX:.4f} mm/px  ({args.canvas_mm} mm / {IMG_PX} px)")
print(f"Min channel:    {MIN_CHANNEL_MM} mm = {MIN_CHANNEL_PX:.1f} px")
print(f"Min wall:       {MIN_WALL_MM} mm = {MIN_WALL_PX:.1f} px\n")

# ── VAE model ───────────────────────────────────────────────────────────────
image_size  = 128
hidden_size = 1024
device      = torch.device("cpu")

class Flatten(nn.Module):
    def forward(self, x): return x.view(x.size(0), -1)

class UnFlatten(nn.Module):
    def forward(self, x): return x.view(x.size(0), hidden_size, 1, 1)

class VAE(nn.Module):
    def __init__(self, z_dim=args.latent_size):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(1, 16,  kernel_size=4, stride=2), nn.ReLU(),
            nn.Conv2d(16, 32, kernel_size=4, stride=2), nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2), nn.ReLU(),
            nn.Conv2d(64, 128,kernel_size=4, stride=2), nn.ReLU(),
            nn.Conv2d(128,256,kernel_size=4, stride=2), nn.ReLU(),
            Flatten()
        )
        self.fc1 = nn.Linear(hidden_size, z_dim)
        self.fc2 = nn.Linear(hidden_size, z_dim)
        self.fc3 = nn.Linear(z_dim, hidden_size)
        self.decoder = nn.Sequential(
            UnFlatten(),
            nn.ConvTranspose2d(hidden_size, 128, kernel_size=5, stride=2), nn.ReLU(),
            nn.ConvTranspose2d(128, 64, kernel_size=5, stride=2), nn.ReLU(),
            nn.ConvTranspose2d(64,  32, kernel_size=5, stride=2), nn.ReLU(),
            nn.ConvTranspose2d(32,  16, kernel_size=6, stride=2), nn.ReLU(),
            nn.ConvTranspose2d(16,   1, kernel_size=6, stride=2), nn.Sigmoid(),
        )

    def decode(self, z):
        return self.decoder(self.fc3(z))

def apply_vf(img, vf):
    flat = img.flatten()
    k    = int((1 - vf) * flat.size)
    thr  = (np.sort(flat)[k] + np.sort(flat)[k-1]) / 2.0
    return (img >= thr).astype(np.float32)

def z_to_img(z_vec, model, vf):
    z_t = torch.from_numpy(z_vec.reshape(1, -1)).float()
    model.eval()
    with torch.no_grad():
        raw = model.decode(z_t).cpu().reshape(image_size, image_size).numpy()
    img = gaussian_filter(raw, sigma=1)
    img = zoom(img, 3, order=3)             # 128 → 384
    img = (img + np.flip(img, axis=1)) / 2  # symmetry
    return apply_vf(img, vf)

# ── Screening ───────────────────────────────────────────────────────────────
def screen(img):
    void_mask  = (img == 0).astype(np.float32)
    solid_mask = (img == 1).astype(np.float32)

    edt_void  = distance_transform_edt(void_mask)
    edt_solid = distance_transform_edt(solid_mask)

    min_ch_px = float(2 * edt_void[edt_void   > 0].min()) if edt_void.max()  > 0 else 0.0
    min_wt_px = float(2 * edt_solid[edt_solid > 0].min()) if edt_solid.max() > 0 else 0.0

    pass_ch = min_ch_px >= MIN_CHANNEL_PX
    pass_wt = min_wt_px >= MIN_WALL_PX

    return {
        'min_channel_px':  round(min_ch_px, 2),
        'min_channel_mm':  round(min_ch_px * MM_PER_PX, 3),
        'min_wall_px':     round(min_wt_px, 2),
        'min_wall_mm':     round(min_wt_px * MM_PER_PX, 3),
        'pass_channel':    pass_ch,
        'pass_wall':       pass_wt,
        'passes':          pass_ch and pass_wt,
        'porosity':        round(float(void_mask.mean()), 4),
    }

# ── Dirs ────────────────────────────────────────────────────────────────────
for d in ['all/png','all/npy','passed/png','passed/npy']:
    os.makedirs(os.path.join(args.output_dir, d), exist_ok=True)

# ── Load model ───────────────────────────────────────────────────────────────
print(f"Loading model from {args.model_path} ...")
model = VAE().to(device)
model.load_state_dict(torch.load(args.model_path, map_location='cpu'))
model.eval()
print("Model loaded ✓\n")

# ── Generate + screen ────────────────────────────────────────────────────────
np.random.seed(args.seed)
latent_vecs = np.random.randn(args.n, args.latent_size).astype(np.float32)

results      = []
passed_count = 0

for i in range(args.n):
    img     = z_to_img(latent_vecs[i], model, args.vf)
    metrics = screen(img)
    metrics['design_id'] = f'design_{i+1:03d}'

    # Save all
    np.save(os.path.join(args.output_dir, f'all/npy/design_{i+1:03d}.npy'), img)
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    fig.patch.set_facecolor('white')
    axes[0].imshow(img, cmap='gray', vmin=0, vmax=1)
    axes[0].set_title(f'Design #{i+1:03d}', fontsize=10, fontweight='bold')
    axes[0].axis('off')
    status = '✓ PASS' if metrics['passes'] else '✗ FAIL'
    color  = 'green' if metrics['passes'] else 'red'
    info   = (f"Min channel: {metrics['min_channel_mm']:.2f} mm "
              f"({'≥' if metrics['pass_channel'] else '<'} {MIN_CHANNEL_MM} mm)\n"
              f"Min wall:    {metrics['min_wall_mm']:.2f} mm "
              f"({'≥' if metrics['pass_wall'] else '<'} {MIN_WALL_MM} mm)\n"
              f"Porosity:    {metrics['porosity']:.3f}\n\n{status}")
    axes[1].text(0.5, 0.5, info, ha='center', va='center', fontsize=11,
                 color=color, transform=axes[1].transAxes,
                 bbox=dict(boxstyle='round', facecolor='#f8f8f8', edgecolor=color, lw=2))
    axes[1].axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(args.output_dir, f'all/png/design_{i+1:03d}.png'),
                dpi=120, bbox_inches='tight', facecolor='white')
    plt.close()

    # Save passed
    if metrics['passes']:
        passed_count += 1
        np.save(os.path.join(args.output_dir, f'passed/npy/design_{i+1:03d}.npy'), img)
        import shutil
        shutil.copy(
            os.path.join(args.output_dir, f'all/png/design_{i+1:03d}.png'),
            os.path.join(args.output_dir, f'passed/png/design_{i+1:03d}.png')
        )

    results.append(metrics)
    status_str = 'PASS' if metrics['passes'] else 'FAIL'
    print(f"  [{i+1:03d}/{args.n}] {status_str}  "
          f"ch={metrics['min_channel_mm']:.2f}mm  "
          f"wt={metrics['min_wall_mm']:.2f}mm")

# ── Save CSV ─────────────────────────────────────────────────────────────────
csv_path = os.path.join(args.output_dir, 'screening_results.csv')
fields = ['design_id','passes','pass_channel','pass_wall',
          'min_channel_mm','min_wall_mm','min_channel_px','min_wall_px','porosity']
with open(csv_path, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in results:
        w.writerow({k: r[k] for k in fields})

# ── Summary plot ──────────────────────────────────────────────────────────────
pass_results = [r for r in results if r['passes']]
fail_results = [r for r in results if not r['passes']]
pass_ch_only = [r for r in results if not r['passes'] and not r['pass_channel'] and r['pass_wall']]
pass_wt_only = [r for r in results if not r['passes'] and r['pass_channel'] and not r['pass_wall']]
fail_both    = [r for r in results if not r['pass_channel'] and not r['pass_wall']]

fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.patch.set_facecolor('white')
fig.suptitle(f'Screening Results  |  {args.n} designs  |  {passed_count} passed ({passed_count/args.n*100:.0f}%)',
             fontsize=13, fontweight='bold')

# Bar chart
cats   = ['Pass both', 'Fail channel only', 'Fail wall only', 'Fail both']
counts = [len(pass_results), len(pass_ch_only), len(pass_wt_only), len(fail_both)]
colors = ['#2ecc71', '#e74c3c', '#e67e22', '#c0392b']
axes[0].bar(cats, counts, color=colors, edgecolor='white', linewidth=1.5)
axes[0].set_ylabel('Count')
axes[0].set_title('Pass/Fail breakdown')
for bar, count in zip(axes[0].patches, counts):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 str(count), ha='center', fontsize=10, fontweight='bold')
plt.setp(axes[0].xaxis.get_majorticklabels(), rotation=20, ha='right')

# Channel width distribution
ch_vals = [r['min_channel_mm'] for r in results]
axes[1].hist(ch_vals, bins=20, color='#3498db', edgecolor='white', alpha=0.8)
axes[1].axvline(MIN_CHANNEL_MM, color='red', lw=2, linestyle='--',
                label=f'Min {MIN_CHANNEL_MM} mm')
axes[1].set_xlabel('Min channel width (mm)')
axes[1].set_ylabel('Count')
axes[1].set_title('Channel width distribution')
axes[1].legend()

# Wall thickness distribution
wt_vals = [r['min_wall_mm'] for r in results]
axes[2].hist(wt_vals, bins=20, color='#e67e22', edgecolor='white', alpha=0.8)
axes[2].axvline(MIN_WALL_MM, color='red', lw=2, linestyle='--',
                label=f'Min {MIN_WALL_MM} mm')
axes[2].set_xlabel('Min wall thickness (mm)')
axes[2].set_ylabel('Count')
axes[2].set_title('Wall thickness distribution')
axes[2].legend()

plt.tight_layout()
plt.savefig(os.path.join(args.output_dir, 'summary.png'),
            dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print(f"\n{'='*50}")
print(f"SCREENING COMPLETE")
print(f"  Total generated:  {args.n}")
print(f"  Passed:           {passed_count} ({passed_count/args.n*100:.1f}%)")
print(f"  Failed:           {args.n - passed_count}")
print(f"{'='*50}")
print(f"\nOutputs saved to: {args.output_dir}/")
print(f"  all/npy/       — all {args.n} designs as .npy")
print(f"  all/png/       — all {args.n} designs with metrics")
print(f"  passed/npy/    — {passed_count} passed designs as .npy")
print(f"  passed/png/    — {passed_count} passed designs")
print(f"  screening_results.csv")
print(f"  summary.png")
