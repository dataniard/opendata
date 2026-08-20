import os
import sys

import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")


@pytest.fixture
def sample_event():
    """Un evento de prueba con todos los campos requeridos."""
    return {
        "event_id": "event_000001",
        "event_time": "2026-07-15 10:30:00",
        "source_system": "web",
        "user_id": "user_001",
        "raw_payload": '{"action": "click", "session_id": "session_1000", "duration": 42}',
        "ingestion_time": "2026-07-15 11:00:00",
        "file_name": "batch_000.json",
    }


@pytest.fixture
def sample_events():
    """Lista de eventos de prueba."""
    import json
    from datetime import datetime, timedelta

    events = []
    for i in range(50):
        events.append({
            "event_id": f"event_{i:06d}",
            "event_time": datetime.now() - timedelta(days=i % 7),
            "source_system": ["mobile", "web", "api", "backend"][i % 4],
            "user_id": f"user_{i % 10:03d}",
            "raw_payload": json.dumps({
                "action": ["click", "view", "purchase", "share"][i % 4],
                "session_id": f"session_{1000 + i}",
                "duration": i * 10,
            }),
            "ingestion_time": datetime.now(),
            "file_name": f"batch_{i // 10:03d}.json",
        })
    return events
