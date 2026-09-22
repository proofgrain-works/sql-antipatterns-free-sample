# SPDX-License-Identifier: MIT
#!/usr/bin/env python3
"""Shared, standard-library-only evaluator embedded in SQL release packages."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sqlite3
import sys
from typing import Any


EXPECTED_SQLITE = "3.53.4"
MINIMUM_PYTHON = (3, 11)


def typed_equal(actual: Any, expected: Any) -> bool:
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            typed_equal(left, right) for left, right in zip(actual, expected)
        )
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(
            typed_equal(actual[key], expected[key]) for key in expected
        )
    return actual == expected


def eqp_semantics(rows: list[tuple[Any, ...]], expected_table: str) -> dict[str, Any]:
    pattern = re.compile(
        r"^(SCAN|SEARCH) (?:TABLE )?([^ ]+)"
        r"(?: USING (?:COVERING )?INDEX ([^ ]+))?(?: \((.*)\))?$"
    )
    matches: list[dict[str, Any]] = []
    for row in rows:
        match = (
            pattern.match(row[3])
            if len(row) == 4 and isinstance(row[3], str)
            else None
        )
        if match is None or match.group(2) != expected_table:
            continue
        matches.append({
            "matcher": "eqp_semantics_v1",
            "access": match.group(1),
            "table": match.group(2),
            "index": match.group(3),
            "constraints": (
                [] if match.group(4) is None else match.group(4).split(" AND ")
            ),
        })
    if len(matches) != 1:
        raise RuntimeError(
            f"EQP semantic node count for {expected_table}: {len(matches)}"
        )
    return matches[0]


def actual_value(rows: list[tuple[Any, ...]], expected: Any) -> Any:
    if isinstance(expected, dict) and expected.get("matcher") == "eqp_semantics_v1":
        return eqp_semantics(rows, str(expected.get("table", "")))
    nested = [list(row) for row in rows]
    if (
        isinstance(expected, list)
        and expected
        and all(isinstance(item, list) for item in expected)
    ):
        return nested
    if len(rows) == 1:
        return list(rows[0])
    if all(len(row) == 1 for row in rows):
        return [row[0] for row in rows]
    return nested


def memory_connection(mode: str) -> sqlite3.Connection:
    isolation_level: str | None = None if mode == "autocommit" else "DEFERRED"
    options: dict[str, Any] = {"isolation_level": isolation_level}
    if tuple(sys.version_info[:2]) >= (3, 12):
        legacy = getattr(sqlite3, "LEGACY_TRANSACTION_CONTROL", None)
        if legacy is None:
            raise SystemExit("legacy_transaction_control=unavailable")
        options["autocommit"] = legacy
    conn = sqlite3.connect(":memory:", **options)
    conn.enable_load_extension(False)

    def authorize(
        action: int,
        _arg1: str | None,
        arg2: str | None,
        _database: str | None,
        _trigger: str | None,
    ) -> int:
        if action in {sqlite3.SQLITE_ATTACH, sqlite3.SQLITE_DETACH}:
            return sqlite3.SQLITE_DENY
        if (
            action == sqlite3.SQLITE_FUNCTION
            and isinstance(arg2, str)
            and arg2.lower() == "load_extension"
        ):
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    conn.set_authorizer(authorize)
    return conn


def require_version() -> None:
    if tuple(sys.version_info[:2]) < MINIMUM_PYTHON:
        raise SystemExit(
            f"python_version={sys.version_info.major}.{sys.version_info.minor} "
            "minimum_python_version=3.11"
        )
    if sqlite3.sqlite_version != EXPECTED_SQLITE:
        raise SystemExit(
            f"sqlite_version={sqlite3.sqlite_version} "
            f"expected_version={EXPECTED_SQLITE}"
        )


def run_assertions(root: Path) -> tuple[int, int]:
    require_version()
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    total = 0
    for case in manifest["cases"]:
        case_root = root / case["path"]
        assertions = json.loads(
            (case_root / "assertions.json").read_text(encoding="utf-8")
        )
        conn = memory_connection("autocommit")
        try:
            try:
                conn.executescript(
                    (case_root / "schema.sql").read_text(encoding="utf-8")
                )
                if assertions["setup"] == "schema_then_good_sql":
                    conn.executescript(
                        (case_root / "good.sql").read_text(encoding="utf-8")
                    )
            except sqlite3.Error as caught:
                raise SystemExit(
                    f"sqlite_version={sqlite3.sqlite_version} case={case['id']} "
                    "assertion=setup matcher=rows_v1 "
                    f"error_code={getattr(caught, 'sqlite_errorcode', None)} "
                    f"error_name={getattr(caught, 'sqlite_errorname', None)} "
                    f"in_transaction={conn.in_transaction}"
                ) from None
            for index, assertion in enumerate(assertions["assertions"], 1):
                matcher = (
                    assertion["expected"].get("matcher", "rows_v1")
                    if isinstance(assertion["expected"], dict)
                    else "rows_v1"
                )
                try:
                    rows = conn.execute(assertion["sql"]).fetchall()
                    actual = actual_value(rows, assertion["expected"])
                except (sqlite3.Error, RuntimeError) as caught:
                    raise SystemExit(
                        f"sqlite_version={sqlite3.sqlite_version} "
                        f"case={case['id']} assertion={index} matcher={matcher} "
                        f"error_code={getattr(caught, 'sqlite_errorcode', None)} "
                        f"error_name={getattr(caught, 'sqlite_errorname', None)} "
                        f"in_transaction={conn.in_transaction}"
                    ) from None
                if not typed_equal(actual, assertion["expected"]):
                    raise SystemExit(
                        f"sqlite_version={sqlite3.sqlite_version} "
                        f"case={case['id']} assertion={index} matcher={matcher} "
                        f"expected={assertion['expected']!r} actual={actual!r} "
                        f"in_transaction={conn.in_transaction}"
                    )
                total += 1
        finally:
            conn.close()
    return len(manifest["cases"]), total


def _source_sql(
    ref: dict[str, Any], case_root: Path, assertions: dict[str, Any]
) -> str:
    if ref["kind"] == "case_field":
        filename = {
            "schema_sql": "schema.sql",
            "bad_sql": "bad.sql",
            "good_sql": "good.sql",
        }[ref["field"]]
        return (case_root / filename).read_text(encoding="utf-8")
    if ref["kind"] == "assertion":
        return str(
            assertions["assertions"][ref["assertion_number"] - 1]["sql"]
        )
    if ref["kind"] == "inline_sql":
        return str(ref["inline_sql"])
    return ""


def run_scenarios(root: Path) -> int:
    require_version()
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    case_meta = {item["id"]: item for item in manifest["cases"]}
    scenario_doc = json.loads(
        (root / "technical-scenarios.json").read_text(encoding="utf-8")
    )
    for scenario in scenario_doc["scenarios"]:
        case = case_meta[scenario["case_id"]]
        case_root = root / case["path"]
        assertions = json.loads(
            (case_root / "assertions.json").read_text(encoding="utf-8")
        )
        conn = memory_connection(scenario["connection_mode"])
        try:
            try:
                for ref in scenario["setup"]:
                    conn.executescript(_source_sql(ref, case_root, assertions))
            except sqlite3.Error as caught:
                raise SystemExit(
                    f"sqlite_version={sqlite3.sqlite_version} "
                    f"case={scenario['case_id']} scenario={scenario['id']} "
                    f"matcher={scenario['matcher']} "
                    f"error_code={getattr(caught, 'sqlite_errorcode', None)} "
                    f"error_name={getattr(caught, 'sqlite_errorname', None)} "
                    f"in_transaction={conn.in_transaction}"
                ) from None
            for step in scenario["steps"]:
                caught: sqlite3.Error | None = None
                actual: Any = None
                try:
                    if step["operation"] == "commit":
                        conn.commit()
                        actual = []
                    elif step["operation"] == "rollback":
                        conn.rollback()
                        actual = []
                    elif step["operation"] == "execute_script":
                        conn.executescript(
                            _source_sql(step["source"], case_root, assertions)
                        )
                        actual = []
                    else:
                        rows = conn.execute(
                            _source_sql(step["source"], case_root, assertions)
                        ).fetchall()
                        actual = actual_value(
                            rows, step["expectation"]["expected"]
                        )
                except sqlite3.Error as exc:
                    caught = exc
                except RuntimeError:
                    raise SystemExit(
                        f"sqlite_version={sqlite3.sqlite_version} "
                        f"case={scenario['case_id']} scenario={scenario['id']} "
                        f"matcher={scenario['matcher']} error_code=None "
                        f"error_name=None in_transaction={conn.in_transaction}"
                    ) from None
                expected = step["expectation"]
                if expected["outcome"] == "success":
                    if caught is not None or not typed_equal(
                        actual, expected["expected"]
                    ):
                        raise SystemExit(
                            f"sqlite_version={sqlite3.sqlite_version} "
                            f"case={scenario['case_id']} scenario={scenario['id']} "
                            f"matcher={scenario['matcher']} "
                            f"expected={expected['expected']!r} actual={actual!r} "
                            f"error_code={getattr(caught, 'sqlite_errorcode', None)} "
                            f"in_transaction={conn.in_transaction}"
                        )
                elif caught is None or (
                    getattr(caught, "sqlite_errorcode", None)
                    != expected["sqlite_error_code"]
                    or getattr(caught, "sqlite_errorname", None)
                    != expected["sqlite_error_name"]
                    or expected["message_token"].lower() not in str(caught).lower()
                ):
                    raise SystemExit(
                        f"sqlite_version={sqlite3.sqlite_version} "
                        f"case={scenario['case_id']} scenario={scenario['id']} "
                        f"matcher={scenario['matcher']} "
                        f"expected_error={expected['sqlite_error_code']}/"
                        f"{expected['sqlite_error_name']} "
                        f"actual_error={getattr(caught, 'sqlite_errorcode', None)}/"
                        f"{getattr(caught, 'sqlite_errorname', None)} "
                        f"in_transaction={conn.in_transaction}"
                    )
                if conn.in_transaction is not step["in_transaction"]:
                    raise SystemExit(
                        f"sqlite_version={sqlite3.sqlite_version} "
                        f"case={scenario['case_id']} scenario={scenario['id']} "
                        f"matcher={scenario['matcher']} "
                        f"expected_in_transaction={step['in_transaction']} "
                        f"actual_in_transaction={conn.in_transaction}"
                    )
            if scenario["recovery"]["operation"] == "rollback":
                conn.rollback()
            if conn.in_transaction is not scenario["recovery"]["in_transaction"]:
                raise SystemExit(
                    f"sqlite_version={sqlite3.sqlite_version} "
                    f"case={scenario['case_id']} scenario={scenario['id']} "
                    f"matcher={scenario['matcher']} "
                    f"expected_in_transaction={scenario['recovery']['in_transaction']} "
                    f"actual_in_transaction={conn.in_transaction}"
                )
            for post in scenario["post_state_assertions"]:
                try:
                    rows = conn.execute(post["sql"]).fetchall()
                    actual = actual_value(rows, post["expected"])
                except (sqlite3.Error, RuntimeError) as caught:
                    raise SystemExit(
                        f"sqlite_version={sqlite3.sqlite_version} "
                        f"case={scenario['case_id']} scenario={scenario['id']} "
                        f"matcher={post['matcher']} "
                        f"error_code={getattr(caught, 'sqlite_errorcode', None)} "
                        f"error_name={getattr(caught, 'sqlite_errorname', None)} "
                        f"in_transaction={conn.in_transaction}"
                    ) from None
                if not typed_equal(actual, post["expected"]):
                    raise SystemExit(
                        f"sqlite_version={sqlite3.sqlite_version} "
                        f"case={scenario['case_id']} scenario={scenario['id']} "
                        f"matcher={post['matcher']} expected={post['expected']!r} "
                        f"actual={actual!r} in_transaction={conn.in_transaction}"
                    )
        finally:
            conn.close()
    return len(scenario_doc["scenarios"])
