import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from ingest_bronze_data import generate_sample_events


REQUIRED_EVENT_FIELDS = [
    "event_id",
    "event_time",
    "source_system",
    "user_id",
    "raw_payload",
    "ingestion_time",
    "file_name",
]

SOURCE_SYSTEMS = ["mobile", "web", "api", "backend"]
ACTION_TYPES = ["click", "view", "purchase", "share"]


class TestGenerateSampleEvents:
    def test_returns_correct_count(self):
        events = generate_sample_events(100)
        assert len(events) == 100

    def test_returns_correct_count_small(self):
        events = generate_sample_events(1)
        assert len(events) == 1

    def test_returns_correct_count_zero(self):
        events = generate_sample_events(0)
        assert len(events) == 0

    def test_default_count_is_1000(self):
        events = generate_sample_events()
        assert len(events) == 1000

    def test_all_required_fields_present(self):
        events = generate_sample_events(10)
        for event in events:
            for field in REQUIRED_EVENT_FIELDS:
                assert field in event, f"Missing field '{field}' in event"

    def test_event_ids_are_unique(self):
        events = generate_sample_events(200)
        ids = [e["event_id"] for e in events]
        assert len(ids) == len(set(ids))

    def test_event_ids_format(self):
        events = generate_sample_events(5)
        for event in events:
            assert event["event_id"].startswith("event_")

    def test_source_systems_valid(self):
        events = generate_sample_events(100)
        for event in events:
            assert event["source_system"] in SOURCE_SYSTEMS

    def test_user_ids_format(self):
        events = generate_sample_events(50)
        for event in events:
            assert event["user_id"].startswith("user_")

    def test_raw_payload_is_valid_json(self):
        events = generate_sample_events(20)
        for event in events:
            payload = json.loads(event["raw_payload"])
            assert isinstance(payload, dict)

    def test_raw_payload_contains_action(self):
        events = generate_sample_events(20)
        for event in events:
            payload = json.loads(event["raw_payload"])
            assert "action" in payload
            assert payload["action"] in ACTION_TYPES

    def test_raw_payload_contains_session_id(self):
        events = generate_sample_events(20)
        for event in events:
            payload = json.loads(event["raw_payload"])
            assert "session_id" in payload

    def test_raw_payload_contains_duration(self):
        events = generate_sample_events(20)
        for event in events:
            payload = json.loads(event["raw_payload"])
            assert "duration" in payload
            assert isinstance(payload["duration"], int)

    def test_file_name_format(self):
        events = generate_sample_events(250)
        for event in events:
            assert event["file_name"].startswith("batch_")
            assert event["file_name"].endswith(".json")
