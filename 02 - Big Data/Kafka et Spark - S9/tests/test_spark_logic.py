"""Tests Spark : parsing/validation (2.1), raisons d'erreur (3.2), agrégations (2.2)."""
from __future__ import annotations

import json

from pyspark.sql import functions as F

from src.common.spark_schema import parse_kafka_stream, split_valid_invalid
from src.consumer import transformations as T
from src.consumer.error_handling import with_error_reason


def _event_json(**overrides) -> str:
    base = {
        "event_id": "e1", "user_id": "u1", "video_id": "v1", "event_type": "PLAY",
        "timestamp": "2026-06-27T12:00:00+00:00", "current_time": 1.0,
        "duration": 10.0, "genre": "action", "device": "mobile",
    }
    base.update(overrides)
    return json.dumps(base)


def _kafka_df(spark, tmp_path, rows):
    """rows: liste de (key, value, partition, offset) -> DataFrame façon source Kafka.

    On passe par un fichier JSON lu par spark.read.json (chemin JVM) plutôt que
    par createDataFrame : ce dernier déclenche un cloudpickle qui plante sur
    Python 3.14 (RecursionError dans la cloudpickle embarquée de pyspark).
    """
    path = tmp_path / "input.json"
    with open(path, "w", encoding="utf-8") as f:
        for key, value, partition, offset in rows:
            f.write(json.dumps({"key": key, "value": value,
                                "partition": partition, "offset": offset}) + "\n")
    df = spark.read.schema(
        "key string, value string, partition int, offset long"
    ).json(str(path))
    return df.withColumn("timestamp", F.current_timestamp())


def _sample_rows():
    return [
        ("u1", _event_json(), 0, 0),                          # valide
        ("u2", "{ pas du json", 0, 1),                        # INVALID_JSON
        ("u3", _event_json(user_id=None), 1, 2),              # MISSING_REQUIRED_FIELD
        ("u4", _event_json(event_type="FOO"), 2, 3),          # BAD_EVENT_TYPE
    ]


def test_split_valid_invalid_counts(spark, tmp_path):
    parsed = parse_kafka_stream(_kafka_df(spark, tmp_path, _sample_rows()))
    valid, invalid = split_valid_invalid(parsed)
    assert valid.count() == 1
    assert invalid.count() == 3


def test_error_reasons(spark, tmp_path):
    parsed = parse_kafka_stream(_kafka_df(spark, tmp_path, _sample_rows()))
    _valid, invalid = split_valid_invalid(parsed)
    reasons = {r["kafka_offset"]: r["error_reason"]
               for r in with_error_reason(invalid).select("kafka_offset", "error_reason").collect()}
    assert reasons[1] == "INVALID_JSON"
    assert reasons[2] == "MISSING_REQUIRED_FIELD"
    assert reasons[3] == "BAD_EVENT_TYPE"


def test_valid_event_has_processing_and_event_time(spark, tmp_path):
    parsed = parse_kafka_stream(_kafka_df(spark, tmp_path, [_sample_rows()[0]]))
    valid, _ = split_valid_invalid(parsed)
    row = valid.select("event_time", "processing_time").collect()[0]
    assert row["event_time"] is not None
    assert row["processing_time"] is not None


def test_video_popularity_counts_views(spark, tmp_path):
    rows = [
        ("u1", _event_json(video_id="v1", event_type="PLAY"), 0, 0),
        ("u2", _event_json(video_id="v1", event_type="PLAY"), 0, 1),
        ("u3", _event_json(video_id="v1", event_type="PAUSE"), 0, 2),
        ("u4", _event_json(video_id="v2", event_type="PLAY"), 0, 3),
    ]
    parsed = parse_kafka_stream(_kafka_df(spark, tmp_path, rows))
    valid, _ = split_valid_invalid(parsed)
    pop = T.video_popularity(valid).collect()
    # fenêtre glissante 10min/5min -> chaque vidéo apparaît dans 2 fenêtres (mêmes comptes)
    v1 = [r for r in pop if r["video_id"] == "v1"]
    v2 = [r for r in pop if r["video_id"] == "v2"]
    assert all(r["views"] == 2 and r["events"] == 3 for r in v1)   # 2 PLAY, 3 events
    assert all(r["views"] == 1 and r["events"] == 1 for r in v2)


def test_genre_analysis_aggregates(spark, tmp_path):
    rows = [
        ("u1", _event_json(genre="action", event_type="PLAY"), 0, 0),
        ("u2", _event_json(genre="action", event_type="PLAY"), 0, 1),
        ("u3", _event_json(genre="drama", event_type="PLAY"), 0, 2),
    ]
    parsed = parse_kafka_stream(_kafka_df(spark, tmp_path, rows))
    valid, _ = split_valid_invalid(parsed)
    res = T.genre_analysis(valid).collect()
    action = [r for r in res if r["genre"] == "action"]
    assert all(r["views"] == 2 for r in action)
