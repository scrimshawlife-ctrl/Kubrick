#!/usr/bin/env python3
from production_surface import run

ACTIONS = {"build", "create", "improve", "audit", "reconcile", "drift", "update", "validate"}

if __name__ == "__main__":
    raise SystemExit(run("design", ACTIONS))
