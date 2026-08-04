#!/usr/bin/env python3
from production_surface import run

ACTIONS = {"shot", "motion", "sequence", "adapt", "qa"}

if __name__ == "__main__":
    raise SystemExit(run("video", ACTIONS))
