#!/usr/bin/env python3
from production_surface import run

ACTIONS = {"create", "improve", "diagnose", "adapt", "continuity-check", "handoff"}

if __name__ == "__main__":
    raise SystemExit(run("script", ACTIONS))
