#!/usr/bin/env python3
"""Autoroute a KiCad 9 board headlessly with Freerouting.

    tools/autoroute.py IN.kicad_pcb OUT.kicad_pcb [--passes N] [--threads N]

Steps: pcbnew Specctra DSN export -> `freerouting` (installed by
tools/kicad_env_setup.sh) -> Specctra SES import -> save OUT. Existing
tracks are kept; Freerouting only adds the missing connections.

The Specctra exporter refuses boards with duplicate reference designators
(this board has two "R21", see analysis F-ledger), so duplicates are renamed
REF_DUP1.. for the round trip and restored before saving. The rename is
never written to IN.

Caveat for this repo: the checked-in .kicad_pcb has no GND pour and is a
stale copy (README "Critical provenance warning"), so routing it is only a
tooling exercise until Trey's real working file arrives.
"""
import argparse, os, subprocess, sys, tempfile

import pcbnew


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--passes", type=int, default=20, help="Freerouting max passes (-mp), default 20")
    ap.add_argument("--threads", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--keep", action="store_true", help="keep the .dsn/.ses next to OUT")
    a = ap.parse_args()

    board = pcbnew.LoadBoard(a.inp)
    board.BuildConnectivity()
    before = board.GetConnectivity().GetUnconnectedCount(True)

    # Temporarily de-duplicate reference designators.
    seen, renamed = set(), []
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref in seen:
            new = f"{ref}_DUP{len(renamed) + 1}"
            fp.SetReference(new); renamed.append((fp, ref))
            print(f"note: duplicate refdes {ref} -> {new} for the DSN round trip", file=sys.stderr)
        seen.add(ref)

    work = os.path.dirname(os.path.abspath(a.out)) if a.keep else tempfile.mkdtemp(prefix="autoroute-")
    stem = os.path.splitext(os.path.basename(a.out))[0]
    dsn, ses = os.path.join(work, stem + ".dsn"), os.path.join(work, stem + ".ses")

    if not pcbnew.ExportSpecctraDSN(board, dsn):
        sys.exit("Specctra DSN export failed (pcbnew gives no reason headless; "
                 "check for duplicate refdes, pads without copper layers, or an open outline)")

    cmd = ["freerouting", "-de", dsn, "-do", ses, "-mp", str(a.passes), "-mt", str(a.threads)]
    print("running:", " ".join(cmd), file=sys.stderr)
    subprocess.run(cmd, check=True)
    if not os.path.exists(ses):
        sys.exit("freerouting produced no .ses file")

    if not pcbnew.ImportSpecctraSES(board, ses):
        sys.exit("Specctra SES import failed")
    for fp, ref in renamed:
        fp.SetReference(ref)

    board.BuildConnectivity()
    after = board.GetConnectivity().GetUnconnectedCount(True)
    pcbnew.SaveBoard(a.out, board)
    print(f"unrouted connections: {before} -> {after}; tracks now {len(board.GetTracks())}; saved {a.out}")


if __name__ == "__main__":
    main()
