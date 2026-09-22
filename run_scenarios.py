#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from pathlib import Path
from sql_evaluator import run_scenarios

if __name__ == "__main__":
    scenarios = run_scenarios(Path(__file__).resolve().parent)
    print(f"PASS: {scenarios} technical scenarios")
