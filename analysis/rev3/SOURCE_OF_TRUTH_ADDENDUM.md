# Rev 3 addendum to SOURCE_OF_TRUTH.md
**Established:** 2026-10-09. `analysis/SOURCE_OF_TRUTH.md` still governs; this records what differs for rev 3.

1. **Ground truth.** `rev3/WavetableController.kicad_pcb` contains the filled GND zone and is the sole copper truth. There are no rev-3 Gerbers; nothing has been fabbed from these files. The dual-truth rule of rev 2 (Gerbers vs KiCad files) does not apply — every pass checks the KiCad files.
2. **Rev-2 finding scoring.** Every rev-2 finding F-001…F-035 gets exactly one of: FIXED (evidence in rev 3), STILL OPEN, REGRESSED (worse), N/A (the circuit no longer exists). Scores live in `FINDINGS.md` here. Nothing silently evaporates.
3. **New findings** are numbered R3-001… in `FINDINGS.md`; per-pass reports use provisional ids (R3-P1-01 …) that the ledger maps.
4. **Blocked sources.** daisy.audio, electrokit.com, cree-led.com and api.github.com are blocked by the session's egress proxy. Where a threshold came from a secondary source (KiCad library symbol, libDaisy source, rev-2 citation, forum), the finding says so. These are the first candidates for re-verification when the primary datasheet is available.
5. **Scratch outputs** live in `kicad_out/rev3/` (git-ignored) and the session scratchpad; reproducible scripts are copied to `analysis/rev3/scripts/`.
