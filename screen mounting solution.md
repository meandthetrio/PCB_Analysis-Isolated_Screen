# Screen Mounting Solution — Crystalfontz CFAL12864G-024W OLED

**Module:** [CFAL12864G-024W](https://www.crystalfontz.com/product/cfal12864g024w-128x64-2-4inch-white-oled-module) — 128×64 2.4" white OLED
**Context:** Bare chip-on-glass (COG) module mounted between a PCB and a metal enclosure with a display cutout.

## Key mechanical facts

| Property | Value |
|---|---|
| Glass outline | 60.5 × 37.0 mm |
| Thickness | 2.15 mm |
| Viewing area | 57.01 × 28.91 mm |
| Active area | 55.01 × 27.46 mm |
| Weight | 9.2 g |
| Connection | FPC ribbon tail into ZIF connector (TE 3-1734839-1 top-contact, or Hirose FH41-31S-0.5SH bottom-contact) |
| Mounting holes | **None** — cannot be screwed down |

## Mounting approach: tape + gasket sandwich

### 1. Adhesive tape to the PCB (primary attachment)
- Frame of thin double-sided adhesive on the PCB where the glass sits:
  - 3M 467MP / 468MP transfer tape (thin), or 3M VHB (adds cushioning)
- Keep-out under the active area — no components or vias under the glass, or add a spacer/foam pad to keep it flat.
- FPC tail folds around into the ZIF connector on the PCB.
- The tape IS the mount — this is how nearly every product using these glass modules does it.

### 2. Foam gasket between glass and metal panel
- Rectangular picture-frame gasket, ~0.5–1 mm compressible foam, around the display opening on the inside of the enclosure.
  - Poron is the classic choice; 3M double-coated foam tape (e.g. 4926) also works.
- When the enclosure closes, the foam lightly compresses against the glass face.
- Four jobs: takes up stack-height tolerance, prevents glass-to-metal contact (glass + rigid metal = cracked display), blocks light leakage around the window, keeps dust out.

### 3. Window sizing
- Bezel opening: bigger than viewing area (57.0 × 28.9 mm), smaller than glass outline (60.5 × 37 mm).
- ~**58 × 30 mm** hides the glass edges and the driver-chip strip while showing the full image.
- The active area is offset toward one side of the glass (driver IC + FPC take up one edge) — center the window on the *viewing area* from the datasheet drawing, not on the glass outline.

## Stack-height calculation

Measure: PCB top surface → inside face of enclosure panel.

```
gap − 2.15 mm (glass) = tape thickness under glass + compressed foam thickness above it
```

- If the gap is large: rigid spacer or 3D-printed carrier frame under the display, keep the foam layer thin.
- Target ~30–50% foam compression — gentle, even pressure only around the border of the glass, never concentrated on a corner.

## Cautions

- **Don't** rely on enclosure clamping alone — vibration lets the glass shift and the FPC fatigues.
- **Don't** hard-clamp the glass rigidly with no compliance — it needs the foam.
- Alternative for serviceability: small 3D-printed or machined bezel frame that captures the glass edges and screws to the PCB (detailed below). For one-offs / small runs, tape + Poron gasket is the proven answer.

## Alternative: 3D-printed bezel frame

A rectangular frame that screws to the PCB and captures the glass — serviceable (no adhesive), precisely located, and sets the correct height to the enclosure window. The glass drops into a pocket from behind; the front lip overhangs the glass edges; the frame screws to the PCB trapping the glass — always with thin foam in the sandwich, never plastic clamped hard on glass.

### Design dimensions

| Feature | Dimension | Notes |
|---|---|---|
| Glass pocket | 61.0 × 37.5 mm | +0.5 mm total clearance over the 60.5 × 37.0 glass; drop-in fit, never press-fit |
| Pocket depth | ~2.0 mm | Glass is 2.15 mm — lip pre-loads slightly onto foam instead of bottoming plastic-on-glass |
| Front lip opening | ~58 × 30 mm | ~1.5 mm overlap per side; larger than 57.0 × 28.9 viewing area so no image crop; hides driver-chip strip |
| FPC slot | Full ribbon width | In the pocket wall on the FPC edge (check datasheet drawing); round/chamfer edges so ribbon doesn't crease when folding to the ZIF |
| Foam | 0.5 mm Poron | Between lip and glass face, ideally also under the glass. Foam grips the display; plastic only sets geometry |
| Mounting | 4× corner bosses, M2 | Heat-set inserts (clean) or M2 self-tappers into 1.7 mm holes. Add matching M2 holes to the PCB around the display footprint |

- The active area is **offset** on the glass — model the opening relative to the viewing area per the datasheet mechanical drawing, not the glass outline.
- Nice extra: alignment pins or a raised rim on the front face that registers into the enclosure window cutout — the screen self-centers and PCB↔enclosure tolerance stacking disappears.

### Printing notes

- **Material:** PETG or ASA. PLA OK for prototypes but creeps under clamping load and softens in a warm enclosure.
- **Orientation:** bezel-face-down on a smooth plate — clean visible face, no supports needed for the pocket.
- **Tolerances:** FDM pockets come out 0.1–0.3 mm undersized. Print just the pocket as a quick test piece and confirm the glass drops in before printing the full frame.
- **Caution:** no plastic may press directly on glass anywhere — every contact on the display face goes through foam. Glass tolerates gentle distributed pressure, fails at hard point contacts.
