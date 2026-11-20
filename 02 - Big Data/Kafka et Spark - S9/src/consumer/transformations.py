"""Transformations et agrégations en fenêtres glissantes (Tâche 2.2).

Chaque fonction prend le flux d'événements *valides* (sortie de
src.common.spark_schema.parse_kafka_stream / split_valid_invalid) et renvoie
un DataFrame streaming agrégé.

Fenêtre par défaut : 10 minutes, calculée toutes les 5 minutes (cf. settings).
Un watermark borne l'état conservé et tolère les événements en léger retard.
"""
from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window

from config import settings


def _sliding_window(duration: str | None = None, slide: str | None = None) -> Column:
    """Colonne window glissante (window/slide depuis settings par défaut)."""
    return F.window(
        F.col("event_time"),
        duration or settings.WINDOW_DURATION,
        slide or settings.SLIDE_DURATION,
    )


def _with_watermark(df: DataFrame) -> DataFrame:
    return df.withWatermark("event_time", settings.WATERMARK_DELAY)


def _flatten_window(df: DataFrame) -> DataFrame:
    """Remplace la struct `window` par deux colonnes lisibles window_start/window_end."""
    return df.withColumn("window_start", F.col("window.start")) \
        .withColumn("window_end", F.col("window.end")) \
        .drop("window")


# ---------------------------------------------------------------------------
# Requête 1 : Popularité des vidéos
# ---------------------------------------------------------------------------
def video_popularity(events: DataFrame) -> DataFrame:
    """Nombre de vues (PLAY) et d'événements par vidéo et par fenêtre."""
    agg = (
        _with_watermark(events)
        .groupBy(_sliding_window(), F.col("video_id"), F.col("genre"))
        .agg(
            F.sum(F.when(F.col("event_type") == "PLAY", 1).otherwise(0)).alias("views"),
            F.count("*").alias("events"),
            F.approx_count_distinct("user_id").alias("unique_users"),
        )
    )
    return _flatten_window(agg)


def top_n_videos(popularity_batch: DataFrame, n: int = 10) -> DataFrame:
    """Top N des vidéos les plus regardées PAR fenêtre (à appliquer sur un micro-batch).

    Le ranking par fenêtre (row_number) n'est pas supporté directement sur un flux ;
    on l'applique sur le DataFrame statique reçu dans foreachBatch (cf. Tâche 2.3).
    """
    w = Window.partitionBy("window_start", "window_end").orderBy(F.col("views").desc())
    return (
        popularity_batch.withColumn("rank", F.row_number().over(w))
        .filter(F.col("rank") <= n)
        .orderBy("window_start", "rank")
    )


# ---------------------------------------------------------------------------
# Requête 2 : Engagement utilisateur
# ---------------------------------------------------------------------------
def user_engagement(events: DataFrame) -> DataFrame:
    """Engagement par utilisateur et par fenêtre.

    watch_time_proxy : amplitude de position visionnée (max-min de current_time).
    Les événements simulés étant des instantanés sans durée explicite, c'est une
    approximation documentée du temps de visionnage.
    """
    agg = (
        _with_watermark(events)
        .groupBy(_sliding_window(), F.col("user_id"))
        .agg(
            F.count("*").alias("events"),
            F.approx_count_distinct("video_id").alias("videos_watched"),
            (F.max("current_time") - F.min("current_time")).alias("watch_time_proxy"),
            F.max("event_time").alias("last_event"),
        )
    )
    return _flatten_window(agg)


def inactive_users(events: DataFrame) -> DataFrame:
    """Utilisateurs inactifs : aucun événement depuis > INACTIVITY_THRESHOLD_MIN minutes.

    Agrégation par utilisateur (sans fenêtre) du dernier event_time, comparée à
    l'horloge courante au moment du micro-batch. À consommer en outputMode("update").
    """
    threshold_s = settings.INACTIVITY_THRESHOLD_MIN * 60
    agg = (
        _with_watermark(events)
        .groupBy(F.col("user_id"))
        .agg(
            F.max("event_time").alias("last_event"),
            F.count("*").alias("events"),
        )
        .withColumn(
            "inactive_seconds",
            F.unix_timestamp(F.current_timestamp()) - F.unix_timestamp("last_event"),
        )
        .filter(F.col("inactive_seconds") > threshold_s)
    )
    return agg


# ---------------------------------------------------------------------------
# Requête 3 : Analyse par genre
# ---------------------------------------------------------------------------
def genre_analysis(events: DataFrame) -> DataFrame:
    """Répartition des visionnages et temps moyen (proxy) par genre et par fenêtre."""
    agg = (
        _with_watermark(events)
        .groupBy(_sliding_window(), F.col("genre"))
        .agg(
            F.count("*").alias("views"),
            F.round(F.avg("current_time"), 2).alias("avg_watch_position"),
            F.approx_count_distinct("user_id").alias("unique_users"),
            F.approx_count_distinct("video_id").alias("unique_videos"),
        )
    )
    return _flatten_window(agg)


# ---------------------------------------------------------------------------
# Requête 4 : Détection d'anomalies
# ---------------------------------------------------------------------------
def anomaly_user_many_videos(events: DataFrame) -> DataFrame:
    """Alerte : utilisateur regardant > N vidéos distinctes en 1 heure."""
    threshold = settings.ANOMALY_USER_VIDEOS_THRESHOLD
    agg = (
        _with_watermark(events)
        .groupBy(
            _sliding_window(settings.ANOMALY_USER_WINDOW, settings.ANOMALY_USER_SLIDE),
            F.col("user_id"),
        )
        .agg(F.approx_count_distinct("video_id").alias("distinct_videos"),
             F.count("*").alias("events"))
        .filter(F.col("distinct_videos") > threshold)
        .withColumn("alert", F.lit("USER_TOO_MANY_VIDEOS"))
    )
    return _flatten_window(agg)


def anomaly_device_flood(events: DataFrame) -> DataFrame:
    """Alerte : > N événements en 5 minutes depuis un même type de device (fenêtre tumbling)."""
    threshold = settings.ANOMALY_DEVICE_THRESHOLD
    agg = (
        _with_watermark(events)
        # fenêtre tumbling = durée sans slide
        .groupBy(F.window(F.col("event_time"), settings.ANOMALY_DEVICE_WINDOW), F.col("device"))
        .agg(F.count("*").alias("events"))
        .filter(F.col("events") > threshold)
        .withColumn("alert", F.lit("DEVICE_EVENT_FLOOD"))
    )
    return _flatten_window(agg)
