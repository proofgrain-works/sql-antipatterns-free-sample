#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from pathlib import Path
from sql_evaluator import run_assertions

if __name__ == "__main__":
    cases, assertions = run_assertions(Path(__file__).resolve().parent)
    print(f"PASS: {cases} cases / {assertions} assertions")
