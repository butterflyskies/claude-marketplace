#!/usr/bin/env python3
"""Report aggregate token and rate-limit data from a Codex rollout JSONL."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AuditError(RuntimeError):
    """Raised when an authoritative rollout event cannot be identified."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", nargs="?", choices=("full", "snapshot", "json"), default="full")
    parser.add_argument(
        "--rollout",
        type=Path,
        help="Explicit rollout JSONL. Otherwise locate CODEX_THREAD_ID below ~/.codex/sessions.",
    )
    return parser.parse_args()


def read_json_line(line: str, path: Path, line_number: int) -> dict[str, Any]:
    try:
        value = json.loads(line)
    except (json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise AuditError(f"invalid JSON in {path} at line {line_number}: {exc}") from exc
    if not isinstance(value, dict):
        raise AuditError(f"non-object JSON in {path} at line {line_number}")
    return value


def rollout_session_ids(path: Path) -> set[str]:
    ids: set[str] = set()
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            record = read_json_line(line, path, line_number)
            if record.get("type") != "session_meta":
                continue
            payload = record.get("payload")
            session_id = payload.get("id") if isinstance(payload, dict) else None
            if not isinstance(session_id, str) or not session_id:
                raise AuditError(f"session_meta id is absent or malformed in {path}")
            ids.add(session_id)
    if not ids:
        raise AuditError(f"no session_meta id in {path}")
    return ids


def rollout_matches(path: Path, thread_id: str) -> bool:
    try:
        return rollout_session_ids(path) == {thread_id}
    except (OSError, AuditError):
        return False


def locate_rollout(explicit: Path | None) -> tuple[Path, bool]:
    if explicit is not None:
        if not explicit.is_file():
            raise AuditError(f"rollout does not exist: {explicit}")
        thread_id = os.environ.get("CODEX_THREAD_ID")
        if thread_id and not rollout_matches(explicit, thread_id):
            raise AuditError("explicit rollout does not uniquely match the current CODEX_THREAD_ID")
        ids = rollout_session_ids(explicit)
        if len(ids) != 1:
            raise AuditError("explicit rollout contains ambiguous session ids")
        return explicit, bool(thread_id)

    thread_id = os.environ.get("CODEX_THREAD_ID")
    if not thread_id:
        raise AuditError("CODEX_THREAD_ID is absent; pass --rollout explicitly")

    root = Path(os.environ.get("TOKEN_AUDIT_CODEX_HOME", str(Path.home() / ".codex"))) / "sessions"
    if not root.is_dir():
        raise AuditError(f"Codex sessions directory does not exist: {root}")

    candidates = sorted(root.rglob("*.jsonl"), key=lambda path: path.stat().st_mtime, reverse=True)
    for path in candidates:
        if rollout_matches(path, thread_id):
            return path, True
    raise AuditError(f"no rollout matched CODEX_THREAD_ID={thread_id}")


def latest_token_event(path: Path) -> dict[str, Any]:
    latest: dict[str, Any] | None = None
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            record = read_json_line(line, path, line_number)
            if record.get("type") != "event_msg":
                continue
            payload = record.get("payload")
            if isinstance(payload, dict) and payload.get("type") == "token_count":
                latest = record
    if latest is None:
        raise AuditError(f"no token_count event in {path}")
    return latest


def count(mapping: dict[str, Any], key: str) -> int:
    value = mapping.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AuditError(f"token_count field {key!r} is absent or not a finite number")
    if isinstance(value, float) and not math.isfinite(value):
        raise AuditError(f"token_count field {key!r} is absent or not a finite number")
    if value < 0 or int(value) != value:
        raise AuditError(f"token_count field {key!r} is negative or nonintegral")
    return int(value)


def canonical_timestamp(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise AuditError("token_count timestamp is malformed")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AuditError("token_count timestamp is malformed") from exc
    if parsed.tzinfo is None:
        raise AuditError("token_count timestamp lacks a timezone")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def strict_window(value: Any, label: str) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise AuditError(f"{label} rate-limit window is malformed")
    used = value.get("used_percent")
    if isinstance(used, bool) or not isinstance(used, (int, float)):
        raise AuditError(f"{label} used_percent is malformed")
    if isinstance(used, float) and not math.isfinite(used):
        raise AuditError(f"{label} used_percent is malformed")
    if not 0 <= used <= 100:
        raise AuditError(f"{label} used_percent is malformed")
    minutes = count(value, "window_minutes")
    if minutes <= 0:
        raise AuditError(f"{label} window_minutes must be positive")
    reset = count(value, "resets_at")
    try:
        datetime.fromtimestamp(reset, timezone.utc)
    except (OverflowError, OSError, ValueError) as exc:
        raise AuditError(f"{label} resets_at is out of range") from exc
    return {"used_percent": float(used), "window_minutes": minutes, "resets_at": reset}


def normalize_limits(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise AuditError("rate_limits is malformed")
    spend = value.get("spend_control_reached")
    if spend is not None and not isinstance(spend, bool):
        raise AuditError("spend_control_reached is malformed")
    reached_type = value.get("rate_limit_reached_type")
    if reached_type is not None and (not isinstance(reached_type, str) or not reached_type):
        raise AuditError("rate_limit_reached_type is malformed")
    return {
        "primary": strict_window(value.get("primary"), "primary"),
        "secondary": strict_window(value.get("secondary"), "secondary"),
        "individual_limit": strict_window(value.get("individual_limit"), "individual_limit"),
        "spend_control_reached": bool(spend),
        "rate_limit_reached": reached_type is not None,
    }


def normalize(record: dict[str, Any]) -> dict[str, Any]:
    payload = record.get("payload")
    if not isinstance(payload, dict):
        raise AuditError("token_count payload is malformed")
    info = payload.get("info")
    if not isinstance(info, dict):
        raise AuditError("token_count payload.info is malformed")
    total = info.get("total_token_usage")
    last = info.get("last_token_usage")
    if not isinstance(total, dict) or not isinstance(last, dict):
        raise AuditError("token usage objects are absent or malformed")

    context_window = count(info, "model_context_window")
    last_input = count(last, "input_tokens")
    cached_input = count(last, "cached_input_tokens")
    last_output = count(last, "output_tokens")
    last_reasoning = count(last, "reasoning_output_tokens")
    if context_window <= 0 or last_input < 0 or cached_input < 0 or cached_input > last_input:
        raise AuditError("token usage invariants failed")

    limits = normalize_limits(payload.get("rate_limits"))
    total_input = count(total, "input_tokens")
    total_cached = count(total, "cached_input_tokens")
    total_output = count(total, "output_tokens")
    total_reasoning = count(total, "reasoning_output_tokens")
    total_tokens = count(total, "total_tokens")
    if total_cached > total_input:
        raise AuditError("cumulative cached input exceeds cumulative input")
    if total_input < last_input or total_cached < cached_input or total_output < last_output or total_reasoning < last_reasoning:
        raise AuditError("cumulative usage is smaller than the latest request")

    return {
        "recorded_at": canonical_timestamp(record.get("timestamp")),
        "context_window": context_window,
        "last_request": {
            "input_tokens": last_input,
            "cached_input_tokens": cached_input,
            "output_tokens": last_output,
            "reasoning_output_tokens": last_reasoning,
            "context_input_percent": last_input / context_window * 100,
            "cache_percent_of_input": (cached_input / last_input * 100) if last_input else 0.0,
        },
        "session_totals": {
            "input_tokens": total_input,
            "cached_input_tokens": total_cached,
            "output_tokens": total_output,
            "reasoning_output_tokens": total_reasoning,
            "total_tokens": total_tokens,
        },
        "rate_limits": limits,
    }


def format_reset(epoch: int) -> str:
    return datetime.fromtimestamp(epoch, timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")


def limit_lines(limits: dict[str, Any] | None) -> list[str]:
    if not limits:
        return ["| Rate limits | not recorded in this event |"]
    rows: list[str] = []
    for key in ("primary", "secondary", "individual_limit"):
        limit = limits.get(key)
        if limit is None:
            continue
        used = limit.get("used_percent")
        window = limit.get("window_minutes")
        label = key.replace("_", " ").title()
        rows.append(
            f"| {label} limit | {used:.0f}% used; window {window} min; resets {format_reset(limit['resets_at'])} |"
        )
    return rows or ["| Rate limits | present, but no supported limit window was recorded |"]


def warnings(data: dict[str, Any]) -> list[str]:
    out: list[str] = []
    context = data["last_request"]["context_input_percent"]
    if context > 70:
        out.append(f"Last-request input is {context:.0f}% of the model context window.")
    limits = data.get("rate_limits")
    if isinstance(limits, dict):
        for key in ("primary", "secondary", "individual_limit"):
            limit = limits.get(key)
            if isinstance(limit, dict):
                used = float(limit["used_percent"])
                if used > 80:
                    out.append(f"{key.replace('_', ' ').title()} rate limit is {used:.0f}% used.")
        if limits.get("spend_control_reached"):
            out.append("Codex reports that spend control has been reached.")
        if limits.get("rate_limit_reached"):
            out.append("Codex reports that a rate limit has been reached.")
    return out


def print_markdown(data: dict[str, Any], include_warnings: bool) -> None:
    last = data["last_request"]
    total = data["session_totals"]
    print(f"## Codex Token Audit — {data['recorded_at'] or 'timestamp unknown'}\n")
    print("| Metric | Recorded value |")
    print("|---|---:|")
    print(
        f"| Last-request input | {last['input_tokens']:,} / {data['context_window']:,} "
        f"({last['context_input_percent']:.1f}%) |"
    )
    print(f"| Cached input in last request | {last['cached_input_tokens']:,} ({last['cache_percent_of_input']:.1f}%) |")
    print(f"| Last-request output | {last['output_tokens']:,} |")
    print(f"| Last-request reasoning output | {last['reasoning_output_tokens']:,} |")
    print(f"| Runtime cumulative tokens (as recorded) | {total['total_tokens']:,} |")
    print(f"| Current-session match | {'verified' if data['current_session_verified'] else 'not verified (explicit rollout)'} |")
    for row in limit_lines(data.get("rate_limits")):
        print(row)
    if include_warnings:
        print("\n### Warnings")
        items = warnings(data)
        if items:
            for item in items:
                print(f"- {item}")
        else:
            print("- None at the configured thresholds.")
    print("\nCost and burn projections omitted: this rollout event has no authoritative cost field.")


def main() -> int:
    args = parse_args()
    try:
        rollout, session_verified = locate_rollout(args.rollout)
        data = normalize(latest_token_event(rollout))
        data["current_session_verified"] = session_verified
    except (AuditError, OSError) as exc:
        print(f"token-audit: {exc}", file=sys.stderr)
        return 2

    if args.mode == "json":
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_markdown(data, include_warnings=args.mode == "full")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
