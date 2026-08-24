from __future__ import annotations

import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "scripts" / "token_audit.py"
SPEC = importlib.util.spec_from_file_location("token_audit", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
token_audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(token_audit)


def token_record(*, timestamp: str = "2026-08-06T00:00:00Z") -> dict[str, object]:
    return {
        "timestamp": timestamp,
        "type": "event_msg",
        "payload": {
            "type": "token_count",
            "info": {
                "total_token_usage": {
                    "input_tokens": 120,
                    "cached_input_tokens": 80,
                    "output_tokens": 30,
                    "reasoning_output_tokens": 10,
                    "total_tokens": 150,
                },
                "last_token_usage": {
                    "input_tokens": 100,
                    "cached_input_tokens": 75,
                    "output_tokens": 20,
                    "reasoning_output_tokens": 5,
                },
                "model_context_window": 200,
            },
            "rate_limits": {
                "primary": {
                    "used_percent": 81,
                    "window_minutes": 300,
                    "resets_at": 1_786_605_710,
                },
                "secondary": None,
                "individual_limit": None,
                "spend_control_reached": False,
                "rate_limit_reached_type": None,
            },
            "prompt_that_must_not_leak": "secret prompt text",
        },
    }


def write_rollout(path: Path, session_id: str, *records: dict[str, object]) -> None:
    rows = [
        {
            "timestamp": "2026-08-06T00:00:00Z",
            "type": "session_meta",
            "payload": {"id": session_id},
        },
        *records,
    ]
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


class TokenAuditTests(unittest.TestCase):
    def test_normalize_reports_only_supported_aggregate_fields(self) -> None:
        data = token_audit.normalize(token_record())

        self.assertEqual(data["recorded_at"], "2026-08-06T00:00:00Z")
        self.assertEqual(data["context_window"], 200)
        self.assertEqual(data["last_request"]["context_input_percent"], 50)
        self.assertEqual(data["last_request"]["cache_percent_of_input"], 75)
        self.assertNotIn("prompt_that_must_not_leak", json.dumps(data))

    def test_latest_token_event_selects_the_last_recorded_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rollout.jsonl"
            write_rollout(
                path,
                "thread-a",
                token_record(timestamp="2026-08-06T00:00:01Z"),
                token_record(timestamp="2026-08-06T00:00:02Z"),
            )

            latest = token_audit.latest_token_event(path)

        self.assertEqual(latest["timestamp"], "2026-08-06T00:00:02Z")

    def test_explicit_rollout_must_match_current_thread_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rollout.jsonl"
            write_rollout(path, "thread-a", token_record())
            with patch.dict(os.environ, {"CODEX_THREAD_ID": "thread-b"}, clear=False):
                with self.assertRaisesRegex(token_audit.AuditError, "does not uniquely match"):
                    token_audit.locate_rollout(path)

    def test_explicit_rollout_without_thread_is_disclosed_as_unverified(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "rollout.jsonl"
            write_rollout(path, "thread-a", token_record())
            with patch.dict(os.environ, {}, clear=True):
                selected, verified = token_audit.locate_rollout(path)

        self.assertEqual(selected, path)
        self.assertFalse(verified)

    def test_automatic_lookup_binds_to_thread_not_newest_unrelated_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sessions = root / "sessions"
            sessions.mkdir()
            wanted = sessions / "wanted.jsonl"
            unrelated = sessions / "newer.jsonl"
            write_rollout(wanted, "thread-a", token_record())
            write_rollout(unrelated, "thread-b", token_record())
            os.utime(unrelated, (wanted.stat().st_atime + 10, wanted.stat().st_mtime + 10))
            with patch.dict(
                os.environ,
                {"CODEX_THREAD_ID": "thread-a", "TOKEN_AUDIT_CODEX_HOME": str(root)},
                clear=True,
            ):
                selected, verified = token_audit.locate_rollout(None)

        self.assertEqual(selected, wanted)
        self.assertTrue(verified)

    def test_schema_drift_and_counter_invariants_fail_closed(self) -> None:
        missing = token_record()
        del missing["payload"]["info"]["model_context_window"]
        with self.assertRaises(token_audit.AuditError):
            token_audit.normalize(missing)

        invalid = token_record()
        invalid["payload"]["info"]["last_token_usage"]["cached_input_tokens"] = 101
        with self.assertRaisesRegex(token_audit.AuditError, "invariants"):
            token_audit.normalize(invalid)

    def test_markdown_output_never_emits_unknown_payload_content(self) -> None:
        data = token_audit.normalize(token_record())
        data["current_session_verified"] = True
        stream = io.StringIO()

        with redirect_stdout(stream):
            token_audit.print_markdown(data, include_warnings=True)

        output = stream.getvalue()
        self.assertIn("Current-session match | verified", output)
        self.assertIn("Primary rate limit is 81% used", output)
        self.assertNotIn("secret prompt text", output)


if __name__ == "__main__":
    unittest.main()
