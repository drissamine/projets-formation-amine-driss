# Auteur : DRISS Amine  —  ESIS 2 (2025-2026)

"""Tests unitaires du générateur d'événements (sans Spark)."""
from __future__ import annotations

from config import settings
from src.common.event_schema import EventGenerator

EXPECTED_FIELDS = {
    "event_id", "user_id", "video_id", "event_type",
    "timestamp", "current_time", "duration", "genre", "device",
}


def test_event_has_exact_schema():
    event = EventGenerator(seed=1).generate()
    assert set(event) == EXPECTED_FIELDS


def test_enumerations_are_valid():
    gen = EventGenerator(seed=2)
    for _ in range(500):
        e = gen.generate()
        assert e["event_type"] in settings.EVENT_TYPES
        assert e["genre"] in settings.GENRES
        assert e["device"] in settings.DEVICES


def test_current_time_never_exceeds_duration():
    gen = EventGenerator(seed=3)
    for _ in range(500):
        e = gen.generate()
        assert 0.0 <= e["current_time"] <= e["duration"]


def test_video_genre_and_duration_are_stable():
    """Un même video_id garde toujours le même genre et la même durée."""
    gen = EventGenerator(seed=4)
    seen: dict[str, tuple] = {}
    for _ in range(1000):
        e = gen.generate()
        key = e["video_id"]
        value = (e["genre"], e["duration"])
        if key in seen:
            assert seen[key] == value
        else:
            seen[key] = value


def test_seed_is_reproducible():
    a = EventGenerator(seed=42).generate()
    b = EventGenerator(seed=42).generate()
    # event_id est un uuid4 (aléatoire), le reste doit être identique
    a.pop("event_id"); b.pop("event_id")
    a.pop("timestamp"); b.pop("timestamp")
    assert a == b
