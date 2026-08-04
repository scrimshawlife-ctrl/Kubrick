#!/usr/bin/env python3
from production_surface import run

ACTIONS = {"prompt", "sequence", "reference", "negative", "adapt", "qa"}

if __name__ == "__main__":
    raise SystemExit(run("image", ACTIONS))
