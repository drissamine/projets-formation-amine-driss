"""Gestion des erreurs : routage des messages invalides vers la dead-letter queue (Tâche 3.2).

Reprend le flux *invalide* produit par split_valid_invalid (JSON illisible, champ
obligatoire manquant, event_type inconnu, timestamp invalide), lui attache une
raison d'erreur, puis le met en forme pour le sink Kafka (colonnes key/value).
"""
from __future__ import annotations

from functools import reduce

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from src.common.spark_schema import REQUIRED_FIELDS, VALID_EVENT_TYPES


def _error_reason() -> Column:
    """Diagnostique la cause d'invalidité (ordre important : JSON illisible d'abord)."""
    missing_required = reduce(
        lambda acc, field: acc | F.col(field).isNull(),
        REQUIRED_FIELDS,
        F.lit(False),
    )
    return (
        F.when(F.col("event_id").isNull(), F.lit("INVALID_JSON"))
        .when(missing_required, F.lit("MISSING_REQUIRED_FIELD"))
        .when(~F.col("event_type").isin(VALID_EVENT_TYPES), F.lit("BAD_EVENT_TYPE"))
        .when(F.col("event_time").isNull(), F.lit("BAD_TIMESTAMP"))
        .otherwise(F.lit("UNKNOWN"))
    )


def with_error_reason(invalid: DataFrame) -> DataFrame:
    return invalid.withColumn("error_reason", _error_reason())


def to_kafka_dlq(invalid: DataFrame) -> DataFrame:
    """Met le flux invalide au format du sink Kafka (key/value) pour la DLQ.

    La valeur est un JSON conservant le message brut et le contexte de l'erreur
    (raison, partition/offset d'origine) pour permettre le rejeu ou l'analyse.
    """
    enriched = with_error_reason(invalid)
    return enriched.select(
        F.col("kafka_key").alias("key"),
        F.to_json(
            F.struct(
                F.col("error_reason").alias("error"),
                F.col("raw_value"),
                F.col("kafka_partition").alias("source_partition"),
                F.col("kafka_offset").alias("source_offset"),
                F.col("kafka_timestamp").cast("string").alias("source_timestamp"),
                F.current_timestamp().cast("string").alias("dlq_time"),
            )
        ).alias("value"),
    )
