# bregma·lambda

A mouse stereotaxic trajectory planner. Plan straight-down or angled implants on
the Allen Mouse Brain Common Coordinate Framework (CCFv3), with corrections
applied so atlas depths and slice positions actually match real-animal
stereotaxic coordinates.

Runs as a static web app: a folder of PNGs, a small annotation binary, a
single HTML file. No build step, no server, no Qt, no WebGL.

Built by [Matias Andina](https://matiasandina.com).

## What it does

- Two orthogonal atlas views (coronal + sagittal) with the target slice picked
  from the AP/ML/DV coordinates.
- Three DV references: local skull (curved, default), bregma plane (flat),
  local brain pial.
- Tilted-probe planning. Enter ML and AP tilt angles; the planner solves the
  entry point on the curved skull surface iteratively and gives the
  along-probe insertion depth.
- Allen region readout at the target and along the probe traversal.
- Tunable bregma offset in (AP, ML, DV) µm so you can calibrate to your strain.
  Calibration sticks in `localStorage`.
- Optional probe width as a semi-transparent band overlay.

## Corrections applied to the atlas

Allen explicitly states CCFv3 is *not* suitable for determining stereotaxic
coordinates (Wang et al., Cell 2020). On every atlas lookup we apply:

1. **Pitch +5°** rotation around bregma to flatten the bregma–lambda plane
   (Pinpoint / Virtual Brain Lab convention).
2. **Per-axis scale**: `in_vivo = (1.031 · ap_atlas, 0.952 · ml_atlas,
   0.885 · dv_atlas)`. DV is the biggest correction (~11.5%).
3. **Bregma offset** in µm relative to the CCF voxel grid; tunable in the UI.

Tune the constants near the top of the JS block if your strain or age
systematically differs.

## Running it locally

```bash
# one-time: install slicer deps and build the atlas
uv venv --python 3.10 .venv
source .venv/bin/activate
uv pip install brainglobe-atlasapi numpy Pillow
python slicer/build_atlas.py    # downloads + slices Allen CCFv3 50 µm

# serve the static site
./run.sh                        # opens http://localhost:8765/
```

The atlas binaries are committed to the repo so the slicer step is optional
for users who just want to run the app.

## Citation

If you use this for published work, cite the underlying atlas and method
papers:

- Wang Q, Ding S-L, Li Y, et al. The Allen Mouse Brain Common Coordinate
  Framework: A 3D Reference Atlas. *Cell* 181(4):936-953.e20 (2020).
- Birman D, Yang B, Lakshmi N, et al. Pinpoint: multi-probe trajectory
  planning for electrophysiology in mice. *eLife* (2024).
- Chon U, Vanselow DJ, Cheng KC, Kim Y. Enhanced and unified anatomical
  labeling for a common mouse brain atlas. *Nat Commun* 10:5067 (2019).

## License

- **Code, UI, slicer:** [CC-BY-NC-ND 4.0](LICENSE) — Attribution, NonCommercial,
  NoDerivatives.
- **Atlas-derived data** (everything under `atlas/`): inherits Allen
  CCFv3's [CC-BY 4.0](atlas/DATA-LICENSE).

## Disclaimer

For research use only. The atlas is an average mouse; real animals vary by
±0.5 mm. Verify on your own animal with bregma–lambda leveling and dura
touch before committing to a target. The author accepts no liability for
botched implants.

## Support

If this saved you a botched implant,
[buy me a coffee](https://buymeacoffee.com/matiasandina).
