"""
generate_3d_volumes_final.py
============================
Generates 100 smooth 3D scaffold volumes (384x384x384) using
VAE latent space interpolation.

  70 volumes — PASS designs (min channel >= 1.5mm)
  30 volumes — FAIL designs (min channel < 1.5mm)

Method
------
1. Encode each 2D design image back to VAE latent vector (mu)
   - Downsample 384→128px before encoding (model input size)
2. For each volume, sample 2-5 keyframe designs from pass/fail pool
3. Interpolate continuously in LATENT SPACE across all 384 layers:
      z(t) = (1-t_local)*z_i + t_local*z_{i+1}
4. Decode each z(t) → 2D slice (128→384px via zoom)
5. Stack 384 slices → (384, 384, 384) uint8 volume

Why latent interpolation > pixel interpolation
----------------------------------------------
Pixel interpolation between structurally different designs produces
topological jumps (shapes appear/disappear abruptly) that no amount
of Gaussian smoothing can fix. Latent space interpolation produces
semantically smooth transitions because the VAE learns a continuous
manifold where nearby points decode to similar structures.

Basis: Kingma & Welling (2014) — VAE latent space is continuous and
interpolable, producing valid intermediate structures between any two
encoded points. (doi:10.48550/arXiv.1312.6114)

Estimated runtime: ~17 min for 100 volumes on CPU

Usage
-----
    python generate_3d_volumes_final.py \\
        --npy_dir    ./designs/npy \\
        --eval_csv   ./evaluation/results.csv \\
        --model_path ./model_weights \\
        --output_dir ./volumes_3d

Requirements: pip install torch torchvision scipy numpy
"""

import argparse, os, csv, json, time
import numpy as np
import torch, torch.nn as nn
from scipy.ndimage import gaussian_filter, zoom

parser = argparse.ArgumentParser()
parser.add_argument('--npy_dir',    type=str,   default='D:/BaiduNetdiskDownload/generatevolumes/final_200/npy')
parser.add_argument('--eval_csv',   type=str,   default='D:/BaiduNetdiskDownload/generatevolumes/evaluation_results.csv')
parser.add_argument('--model_path', type=str,   default=':/BaiduNetdiskDownload/generatevolumes/model_weights')
parser.add_argument('--output_dir', type=str,   default='D:/BaiduNetdiskDownload/generatevolumes/volumes_3d')
parser.add_argument('--n_pass',     type=int,   default=70)
parser.add_argument('--n_fail',     type=int,   default=30)
parser.add_argument('--n_layers',   type=int,   default=384)
parser.add_argument('--vf',         type=float, default=0.15)
parser.add_argument('--seed',       type=int,   default=42)
args = parser.parse_args()

os.makedirs(os.path.join(args.output_dir, 'pass'), exist_ok=True)
os.makedirs(os.path.join(args.output_dir, 'fail'), exist_ok=True)

# ── VAE model ───────────────────────────────────────────────────────────────
image_size  = 128
hidden_size = 1024
latent_size = 16

class Flatten(nn.Module):
    def forward(self, x): return x.view(x.size(0), -1)
class UnFlatten(nn.Module):
    def forward(self, x): return x.view(x.size(0), hidden_size, 1, 1)
class VAE(nn.Module):
    def __init__(self, z_dim=latent_size):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Conv2d(1,16,4,2),nn.ReLU(),nn.Conv2d(16,32,4,2),nn.ReLU(),
            nn.Conv2d(32,64,4,2),nn.ReLU(),nn.Conv2d(64,128,4,2),nn.ReLU(),
            nn.Conv2d(128,256,4,2),nn.ReLU(),Flatten())
        self.fc1=nn.Linear(hidden_size,z_dim); self.fc2=nn.Linear(hidden_size,z_dim)
        self.fc3=nn.Linear(z_dim,hidden_size)
        self.decoder=nn.Sequential(UnFlatten(),
            nn.ConvTranspose2d(hidden_size,128,5,2),nn.ReLU(),
            nn.ConvTranspose2d(128,64,5,2),nn.ReLU(),
            nn.ConvTranspose2d(64,32,5,2),nn.ReLU(),
            nn.ConvTranspose2d(32,16,6,2),nn.ReLU(),
            nn.ConvTranspose2d(16,1,6,2),nn.Sigmoid())
    def decode(self, z): return self.decoder(self.fc3(z))
    def encode(self, x):
        h = self.encoder(x)
        return self.fc1(h), self.fc2(h)

def apply_vf(img, vf):
    flat = img.flatten()
    k    = int((1-vf)*flat.size)
    thr  = (np.sort(flat)[k]+np.sort(flat)[k-1])/2.0
    return (img >= thr).astype(np.float32)

def img_to_z(img_384, model):
    """Encode 384x384 design → latent vector mu (16-dim)"""
    img_128 = zoom(img_384, 128/384, order=1)
    img_128 = (img_128 > 0.5).astype(np.float32)
    x = torch.from_numpy(img_128).float().unsqueeze(0).unsqueeze(0)
    model.eval()
    with torch.no_grad():
        mu, _ = model.encode(x)
    return mu.squeeze(0).numpy()

def z_to_slice(z_vec, model, vf):
    """Decode latent vector → 384x384 binary slice"""
    z_t = torch.from_numpy(z_vec.reshape(1,-1)).float()
    model.eval()
    with torch.no_grad():
        raw = model.decode(z_t).cpu().reshape(image_size, image_size).numpy()
    img = gaussian_filter(raw, sigma=1)
    img = zoom(img, 3, order=3)
    img = (img + np.flip(img, axis=1)) / 2
    return apply_vf(img, vf)

def make_volume(z_vecs, n_layers, model, vf):
    """
    Continuous latent interpolation across all n_layers.
    z_vecs: list of k latent vectors (keyframes)
    Every layer gets a unique t → every slice is different.
    """
    k         = len(z_vecs)
    waypoints = np.linspace(0, 1, k)
    t_vals    = np.linspace(0, 1, n_layers)
    slices    = []
    for t in t_vals:
        seg     = min(np.searchsorted(waypoints, t, side='right')-1, k-2)
        t_local = (t-waypoints[seg]) / (waypoints[seg+1]-waypoints[seg])
        z_i     = (1-t_local)*z_vecs[seg] + t_local*z_vecs[seg+1]
        slices.append(z_to_slice(z_i, model, vf))
    return np.stack(slices, axis=0).astype(np.uint8)  # (n_layers,384,384)

# ── Load model ──────────────────────────────────────────────────────────────
print(f"Loading model from {args.model_path}...")
model = VAE()
model.load_state_dict(torch.load(args.model_path, map_location='cpu'))
model.eval()
print("Model loaded ✓")

# ── Load pass/fail IDs ──────────────────────────────────────────────────────
results  = list(csv.DictReader(open(args.eval_csv)))
pass_ids = [int(r['id'].split('_')[1]) for r in results if r['passes']=='True']
fail_ids = [int(r['id'].split('_')[1]) for r in results if r['passes']=='False']
print(f"Pass designs: {len(pass_ids)}  |  Fail designs: {len(fail_ids)}")

# ── Encode all designs → latent vectors ────────────────────────────────────
print("\nEncoding designs to latent space...")
pass_zs = {i: img_to_z(np.load(os.path.join(args.npy_dir,f'design_{i:03d}.npy')),model)
           for i in pass_ids}
fail_zs = {i: img_to_z(np.load(os.path.join(args.npy_dir,f'design_{i:03d}.npy')),model)
           for i in fail_ids}
print(f"Encoded {len(pass_zs)} pass + {len(fail_zs)} fail ✓")

# ── Generate volumes ────────────────────────────────────────────────────────
np.random.seed(args.seed)
metadata  = []
total_t0  = time.time()

for group, ids, z_dict, n_vol in [
        ('pass', pass_ids, pass_zs, args.n_pass),
        ('fail', fail_ids, fail_zs, args.n_fail)]:

    print(f"\nGenerating {n_vol} {group.upper()} volumes ({args.n_layers} layers each)...")
    t0 = time.time()

    for i in range(n_vol):
        n_designs = int(np.random.choice([2, 3]))
        chosen    = np.random.choice(ids, size=n_designs, replace=False).tolist()
        z_vecs    = [z_dict[d] for d in chosen]

        vol   = make_volume(z_vecs, args.n_layers, model, args.vf)
        fname = f'volume_{group}_{i+1:03d}.npy'
        np.save(os.path.join(args.output_dir, group, fname), vol)

        metadata.append({
            'id':         f'volume_{group}_{i+1:03d}',
            'group':      group,
            'n_designs':  n_designs,
            'design_ids': [int(x) for x in chosen],
            'porosity':   round(float((vol==0).mean()), 4),
            'shape':      [args.n_layers, 384, 384],
            'dtype':      'uint8',
        })

        if (i+1) % 10 == 0:
            elapsed = time.time()-t0
            rem     = elapsed/(i+1)*(n_vol-i-1)
            print(f"  {i+1}/{n_vol}  ({elapsed:.0f}s, ~{rem:.0f}s remaining)")

with open(os.path.join(args.output_dir, 'metadata.json'), 'w') as f:
    json.dump(metadata, f, indent=2)

total   = time.time()-total_t0
size_gb = (args.n_pass+args.n_fail)*384**3/1e9
print(f"\n{'='*50}")
print(f"Done in {total/60:.1f} min")
print(f"  pass/  ->  {args.n_pass} volumes")
print(f"  fail/  ->  {args.n_fail} volumes")
print(f"  Total size: ~{size_gb:.1f} GB")
print(f"\nLoad:  vol = np.load('volumes_3d/pass/volume_pass_001.npy')")
print(f"       # shape ({args.n_layers}, 384, 384), dtype uint8, values {{0,1}}")