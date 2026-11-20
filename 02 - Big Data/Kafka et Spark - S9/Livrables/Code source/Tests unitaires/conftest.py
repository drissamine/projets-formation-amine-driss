# Auteur : DRISS Amine  —  ESIS 2 (2025-2026)

"""Fixtures pytest partagées : session Spark locale pour les tests (sans Kafka)."""
from __future__ import annotations

import pytest

from config import settings


@pytest.fixture(scope="session")
def spark():
    settings.ensure_java_home()
    settings.ensure_hadoop_home()
    from pyspark.sql import SparkSession

    session = (
        SparkSession.builder.appName("tests")
        .master("local[2]")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    session.sparkContext.setLogLevel("ERROR")
    yield session
    session.stop()
