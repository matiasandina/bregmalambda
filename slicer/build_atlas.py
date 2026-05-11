"""Render Allen CCF (50 um) into 2D PNG slices + coords.json for the planner.

CCF axes (brainglobe convention): (AP, DV, ML), origin at anterior/dorsal/left,
all increase along their axis. Bregma in CCF (Chon 2019, used by Pinpoint):
AP=5400 um, DV=332 um, ML=5700 um.

Stereotaxic -> CCF (um):
    ccf_AP = bregma_AP - stereo_AP   (stereo +AP is anterior)
    ccf_DV = bregma_DV + stereo_DV   (stereo +DV is ventral, from skull)
    ccf_ML = bregma_ML + stereo_ML   (stereo +ML is right)
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image
from brainglobe_atlasapi import BrainGlobeAtlas

ATLAS_NAME = "allen_mouse_50um"
BREGMA_CCF_UM = {"AP": 5400, "DV": 332, "ML": 5700}

OUT = Path(__file__).resolve().parent.parent / "atlas"
OUT.mkdir(parents=True, exist_ok=True)


def to_uint8(vol: np.ndarray) -> np.ndarray:
    v = vol.astype(np.float32)
    lo, hi = np.percentile(v[v > 0], [1, 99.5]) if (v > 0).any() else (0, 1)
    v = np.clip((v - lo) / max(hi - lo, 1e-6), 0, 1)
    return (v * 255).astype(np.uint8)


def main() -> None:
    atlas = BrainGlobeAtlas(ATLAS_NAME)
    ref = atlas.reference  # (AP, DV, ML)
    ann = atlas.annotation
    res_um = atlas.resolution[0]  # isotropic 50
    print(f"Atlas shape (AP, DV, ML) = {ref.shape}, resolution = {res_um} um")

    ref8 = to_uint8(ref)

    # Coronal: fixed AP, image axes (ML horizontal, DV vertical)
    cor_dir = OUT / "coronal"
    cor_dir.mkdir(exist_ok=True)
    for i in range(ref.shape[0]):
        img = ref8[i, :, :]  # (DV, ML)
        Image.fromarray(img).save(cor_dir / f"{i:04d}.png")

    # Sagittal: fixed ML, image axes (AP horizontal, DV vertical).
    # Stereotaxic +AP is to the right in figures, so flip horizontally
    # (CCF AP increases posteriorly; we want anterior on the right).
    sag_dir = OUT / "sagittal"
    sag_dir.mkdir(exist_ok=True)
    for k in range(ref.shape[2]):
        img = ref8[:, :, k].T  # (DV, AP)
        img = np.fliplr(img)  # anterior on the right
        Image.fromarray(img).save(sag_dir / f"{k:04d}.png")

    # Horizontal: fixed DV, image axes (ML horizontal, AP vertical with anterior up)
    hor_dir = OUT / "horizontal"
    hor_dir.mkdir(exist_ok=True)
    for j in range(ref.shape[1]):
        img = ref8[:, j, :]  # (AP, ML)
        img = np.flipud(img)  # anterior up
        Image.fromarray(img).save(hor_dir / f"{j:04d}.png")

    # Brain surface DV maps: for each (AP, ML), the topmost (smallest DV index)
    # and deepest (largest DV index) voxel where annotation > 0.
    # Top is used for "DV from brain" mode; bottom is shown so the user can see
    # the atlas brain depth at that column and catch out-of-volume targets.
    nonzero = ann > 0
    has_any = nonzero.any(axis=1)  # (AP, ML)
    top_idx = np.argmax(nonzero, axis=1)
    # bottom = last True index = (DV - 1) - argmax(reversed)
    bot_idx = ann.shape[1] - 1 - np.argmax(nonzero[:, ::-1, :], axis=1)
    surface_dv_idx = np.where(has_any, top_idx, -1).astype(np.int16)
    bottom_dv_idx  = np.where(has_any, bot_idx, -1).astype(np.int16)
    np.save(OUT / "brain_surface_dv_idx.npy", surface_dv_idx)
    np.save(OUT / "brain_bottom_dv_idx.npy",  bottom_dv_idx)
    # JSON-friendly downsampled (every 2nd voxel) for the browser
    ds_top = surface_dv_idx[::2, ::2].tolist()
    ds_bot = bottom_dv_idx[::2, ::2].tolist()
    (OUT / "brain_surface_dv_idx.json").write_text(json.dumps({
        "step_voxels": 2, "data": ds_top,
        "shape_ap_ml": list(surface_dv_idx[::2, ::2].shape),
        "bottom": ds_bot,
    }))

    # Region annotation volume, downsampled to 100 um for the browser.
    # Saved as raw little-endian uint32 in (AP, DV, ML) order.
    ann_ds = ann[::2, ::2, ::2].astype(np.uint32)
    ann_ds.tofile(OUT / "annotation_100um.u32.bin")
    print(f"Annotation volume (100 µm) shape = {ann_ds.shape}, "
          f"unique structures in volume = {len(np.unique(ann_ds))}")

    # Structure dictionary: id -> {acronym, name}. Pulled from brainglobe.
    # Build it from the structures in the volume so we don't ship the full
    # multi-thousand-row dict for unused species.
    used_ids = set(int(x) for x in np.unique(ann_ds).tolist())
    struct_dict = {}
    for s in atlas.structures.values():
        sid = int(s["id"])
        if sid in used_ids:
            struct_dict[sid] = {
                "acronym": s["acronym"],
                "name": s["name"],
            }
    (OUT / "structures.json").write_text(json.dumps(struct_dict))
    print(f"Wrote {len(struct_dict)} structures to structures.json")

    coords = {
        "atlas": ATLAS_NAME,
        "resolution_um": int(res_um),
        "shape": {"AP": ref.shape[0], "DV": ref.shape[1], "ML": ref.shape[2]},
        "annotation_100um": {
            "shape": list(ann_ds.shape),  # (AP, DV, ML) at 100 µm
            "dtype": "uint32",
            "file":  "annotation_100um.u32.bin",
        },
        "bregma_ccf_um": BREGMA_CCF_UM,
        "stereo_to_ccf_um": {
            "ccf_AP": "bregma.AP - stereo.AP",
            "ccf_DV": "bregma.DV + stereo.DV",
            "ccf_ML": "bregma.ML + stereo.ML",
        },
        "views": {
            "coronal": {
                "fixed_axis": "AP",
                "n_slices": ref.shape[0],
                "image_axes": {"x": "ML", "y": "DV"},
                "image_size_px": [ref.shape[2], ref.shape[1]],
                "x_flipped": False,
                "y_flipped": False,
            },
            "sagittal": {
                "fixed_axis": "ML",
                "n_slices": ref.shape[2],
                "image_axes": {"x": "AP", "y": "DV"},
                "image_size_px": [ref.shape[0], ref.shape[1]],
                "x_flipped": True,
                "y_flipped": False,
                "note": "image is flipped LR so anterior is on the right",
            },
            "horizontal": {
                "fixed_axis": "DV",
                "n_slices": ref.shape[1],
                "image_axes": {"x": "ML", "y": "AP"},
                "image_size_px": [ref.shape[2], ref.shape[0]],
                "x_flipped": False,
                "y_flipped": True,
                "note": "image is flipped UD so anterior is at the top",
            },
        },
    }
    (OUT / "coords.json").write_text(json.dumps(coords, indent=2))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
