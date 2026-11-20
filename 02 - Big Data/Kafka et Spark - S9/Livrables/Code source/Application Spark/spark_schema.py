# Auteur : DRISS Amine  —  ESIS 2 (2025-2026)

"""Schéma Spark des événements de streaming + helpers de parsing/validation (Tâche 2.1)."""
from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, StringType, StructField, StructType

# Schéma strict correspondant au JSON produit par le producteur
EVENT_SCHEMA = StructType(
    [
        StructField("event_id", StringType(), nullable=False),
        StructField("user_id", StringType(), nullable=False),
        StructField("video_id", StringType(), nullable=False),
        StructField("event_type", StringType(), nullable=False),
        StructField("timestamp", StringType(), nullable=False),
        StructField("current_time", DoubleType(), nullable=True),
        StructField("duration", DoubleType(), nullable=True),
        StructField("genre", StringType(), nullable=True),
        StructField("device", StringType(), nullable=True),
    ]
)

# Champs obligatoires : un événement est invalide si l'un d'eux est null
REQUIRED_FIELDS = ["event_id", "user_id", "video_id", "event_type", "timestamp"]
VALID_EVENT_TYPES = ["PLAY", "PAUSE", "STOP", "SEEK"]


def parse_kafka_stream(kafka_df: DataFrame) -> DataFrame:
    """Transforme le flux brut Kafka en colonnes typées.

    Conserve les métadonnées Kafka (key/partition/offset) et la valeur brute
    (raw_value) afin de pouvoir router les messages invalides vers la DLQ.
    """
    return (
        kafka_df.select(
            F.col("key").cast("string").alias("kafka_key"),
            F.col("partition").alias("kafka_partition"),
            F.col("offset").alias("kafka_offset"),
            F.col("timestamp").alias("kafka_timestamp"),
            F.col("value").cast("string").alias("raw_value"),
        )
        # from_json renvoie une struct null si le JSON est illisible
        .withColumn("data", F.from_json(F.col("raw_value"), EVENT_SCHEMA))
        # Colonnes métier à plat
        .select("kafka_key", "kafka_partition", "kafka_offset", "kafka_timestamp",
                "raw_value", "data.*")
        # event_time : timestamp métier (pour les fenêtres) ; processing_time : ingestion Spark
        .withColumn("event_time", F.to_timestamp(F.col("timestamp")))
        .withColumn("processing_time", F.current_timestamp())
    )


def validity_condition() -> Column:
    """Condition booléenne : True si l'événement est valide."""
    cond = F.col("event_id").isNotNull()  # struct parsée (JSON lisible)
    for field in REQUIRED_FIELDS:
        cond = cond & F.col(field).isNotNull()
    cond = cond & F.col("event_type").isin(VALID_EVENT_TYPES)
    cond = cond & F.col("event_time").isNotNull()
    return cond


def split_valid_invalid(parsed_df: DataFrame) -> tuple[DataFrame, DataFrame]:
    """Sépare le flux en (événements valides, événements invalides pour la DLQ)."""
    cond = validity_condition()
    valid = parsed_df.filter(cond)
    invalid = parsed_df.filter(~cond | cond.isNull())
    return valid, invalid
