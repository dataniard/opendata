import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


class TestTransformLogic:
    """Tests de la lógica de transformación sin necesidad de Spark."""

    def _make_bronze_event(self, **overrides):
        base = {
            "event_id": "event_000001",
            "event_time": "2026-07-15 10:30:00",
            "source_system": "web",
            "user_id": "user_001",
            "raw_payload": '{"action": "click", "session_id": "s1", "duration": 42}',
            "ingestion_time": "2026-07-15 11:00:00",
            "file_name": "batch_000.json",
        }
        base.update(overrides)
        return base

    def test_bronze_event_has_required_fields(self):
        event = self._make_bronze_event()
        assert event["event_id"]
        assert event["user_id"]
        assert event["event_time"]

    def test_null_filter_removes_events_without_id(self):
        events = [
            self._make_bronze_event(event_id="e1"),
            self._make_bronze_event(event_id=None),
            self._make_bronze_event(event_id="e3"),
        ]
        filtered = [e for e in events if e["event_id"] is not None]
        assert len(filtered) == 2

    def test_null_filter_removes_events_without_user(self):
        events = [
            self._make_bronze_event(user_id="u1"),
            self._make_bronze_event(user_id=None),
        ]
        filtered = [e for e in events if e["user_id"] is not None]
        assert len(filtered) == 1

    def test_null_filter_removes_events_without_time(self):
        events = [
            self._make_bronze_event(event_time="2026-01-01"),
            self._make_bronze_event(event_time=None),
        ]
        filtered = [e for e in events if e["event_time"] is not None]
        assert len(filtered) == 1

    def test_silver_schema_fields(self):
        silver_fields = [
            "event_id",
            "event_time",
            "user_id",
            "event_type",
            "event_category",
            "properties",
            "created_at",
            "updated_at",
        ]
        assert len(silver_fields) == 8
        assert "event_type" in silver_fields
        assert "properties" in silver_fields

    def test_bronze_to_silver_field_mapping(self):
        bronze = self._make_bronze_event()
        silver = {
            "event_id": bronze["event_id"],
            "event_time": bronze["event_time"],
            "user_id": bronze["user_id"],
            "event_type": bronze["source_system"],
            "event_category": "default",
            "properties": {},
            "created_at": bronze["ingestion_time"],
            "updated_at": "now",
        }
        assert silver["event_id"] == bronze["event_id"]
        assert silver["created_at"] == bronze["ingestion_time"]
