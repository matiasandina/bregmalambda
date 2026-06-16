# Changelog

All notable changes to **bregma·lambda** are documented here. The format
loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning is light-touch — bumps mark user-visible feature batches, not
strict SemVer.

## [v0.3] — 2026-05-29

Big feature batch covering optogenetics, onboarding, layout, and exports.

### Added
- **Optogenetic light-spread overlay** (Kubelka–Munk model, Aravanis 2007 /
  Yizhar 2011; equivalent to the Stanford Deisseroth-lab calculator).
  Heatmap + iso-contours showing predicted mW/mm² isolevels from a
  flat-cut multimode fiber at the probe tip; tip irradiance, axial depth
  at threshold, lateral radius, and illuminated volume readout.
- **Wavelength-tinted monochrome heatmap** — blue for 473 nm, green for
  532 nm, amber for 589 nm, red for 635 nm; iso-lines white for
  legibility over any tint.
- **Custom-wavelength entry** with S interpolated from the published
  anchors and a visible-spectrum hue (so 561 nm renders green, etc.).
- **Bilateral toggle** — mirrors the probe across the midline on the
  coronal view and sums irradiance per pixel (incoherent light is
  additive), so the overlap zone over midline structures (PVN,
  anterior POA, BNST, MS/DBB, etc.) glows brighter. Per-fiber
  iso-contours are shown; hover reports the summed in-plane value.
- **Onboarding spotlight tour** — 8 steps highlighting real UI
  elements; auto-shows on first visit, reopenable from the `? Tour`
  button.
- **Drag-to-resize canvas** via the bottom-right golden bracket:
  widens the centre column by lifting the page cap and reclaiming
  side-panel width. Persists across sessions; double-click resets.
- **Sidebar groups collapsible** with high-contrast headers.
- **Exports**
  - Per-view PNG with a baked-in caption strip (target coords, DV
    reference, wavelength, power, bilateral) and bregma·lambda
    branding.
  - Composite PNG with coronal | sagittal side-by-side, per-view
    labels, shared bottom caption.
  - **Share-as-URL**: 20 input fields serialize to the URL hash on
    every render; pasting the link restores the exact planning state.
  - **Traversal CSV**: regions along the trajectory as
    `index, AP_mm, ML_mm, DV_skull_mm, acronym, region`.

### Changed
- Main grid capped at 1800 px with auto margins for comfortable
  side padding on wide displays (was 1400; reverted from no-cap).
- Right-panel cards flattened (transparent background, smaller type)
  so they stop competing with the canvases.

### Fixed
- Header promoted to its own stacking context (`position: relative`
  + `z-index: 100`) so the export dropdown no longer sinks behind
  the columns and silently closes.

## [v0.2] — 2026-05 (retroactive, not tagged)

- Atlas upscaled to 25 µm; region-outline overlay with hover region
  IDs and acronym/name tooltips.
- Initial width cap on the main grid (later replaced).

## [v0.1] — initial public release (retroactive)

- Coronal + sagittal stereotaxic views over Allen CCFv3 with the
  Pinpoint correction stack: pitch +5°, per-axis scale
  (AP 1.031 / ML 0.952 / DV 0.885), Chon 2019 bregma offset.
- Tilted-probe planning (ML + AP tilt), three DV references
  (curved skull / bregma plane / brain pial).
- Region readout at target, probe traversal, optional probe-width
  band overlay.
- Tunable bregma offset in localStorage.
