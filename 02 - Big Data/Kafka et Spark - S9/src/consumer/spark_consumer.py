"""Consommateur Spark Structured Streaming (Tâche 2.1).

Lit le topic Kafka, parse + valide le JSON, ajoute les timestamps de traitement,
puis affiche en console les flux valides et invalides.

Lancement (depuis la racine du projet) :
    # Traite le backlog existant puis s'arrête (idéal pour valider)
    python -m src.consumer.spark_consumer --once

    # Streaming continu
    python -m src.consumer.spark_consumer

Le connecteur Kafka est téléchargé automatiquement via spark.jars.packages
(nécessite un accès internet au premier lancement).
"""
from __future__ import annotations

import argparse
import os
import sys
import threading

from pyspark.sql import DataFrame, SparkSession

from config import settings
from src.common.spark_schema import parse_kafka_stream, split_valid_invalid

# Doit correspondre à la version de PySpark (3.5.x) et à Scala 2.12
KAFKA_CONNECTOR = "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1"

# Bannière d'initialisation que pyspark imprime sur stderr en mode interpréteur.
# Ce ne sont pas des avertissements : pyspark reconfigure log4j2 lui-même, donc
# ni un fichier log4j2.properties ni -Dlog4j.configurationFile ne les suppriment.
# On filtre ces 2 lignes exactes du flux stderr (tout le reste passe, erreurs incluses).
_BANNER_SNIPPETS = (
    'Setting default log level to',
    "To adjust logging level use sc.setLogLevel",
)
_stderr_filter_installed = False


def _install_stderr_filter() -> None:
    """Redirige stderr vers un filtre qui retire la bannière pyspark.

    À appeler AVANT de lancer la JVM : celle-ci hérite du descripteur filtré.
    """
    global _stderr_filter_installed
    if _stderr_filter_installed:
        return
    _stderr_filter_installed = True

    sys.stderr.flush()
    orig_fd = os.dup(2)          # vrai stderr conservé
    read_fd, write_fd = os.pipe()
    os.dup2(write_fd, 2)         # tout ce qui écrit sur fd 2 part dans le pipe
    os.close(write_fd)

    def _pump() -> None:
        buf = b""
        while True:
            try:
                chunk = os.read(read_fd, 4096)
            except OSError:
                break
            if not chunk:
                break
            buf += chunk
            while b"\n" in buf:
                raw, buf = buf.split(b"\n", 1)
                text = raw.decode("utf-8", "replace")
                if any(s in text for s in _BANNER_SNIPPETS):
                    continue
                os.write(orig_fd, (text + "\n").encode("utf-8", "replace"))
        if buf:
            os.write(orig_fd, buf)

    threading.Thread(target=_pump, name="stderr-filter", daemon=True).start()


def build_spark(app_name: str = "streaming-consumer") -> SparkSession:
    settings.ensure_java_home()
    settings.ensure_hadoop_home()
    _install_stderr_filter()
    spark = (
        SparkSession.builder.appName(app_name)
        .config("spark.jars.packages", KAFKA_CONNECTOR)
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    _silence_shutdown_noise(spark)
    return spark


def _silence_shutdown_noise(spark: SparkSession) -> None:
    """Coupe les ERROR cosmétiques émis à la fermeture de la JVM sous Windows.

    À l'arrêt, deux shutdown hooks tentent de supprimer le même dossier temp ->
    NoSuchFileException. C'est sans impact ; on met ces loggers à OFF (log4j2).
    """
    try:
        jvm = spark._jvm
        configurator = jvm.org.apache.logging.log4j.core.config.Configurator
        off = jvm.org.apache.logging.log4j.Level.OFF
        for logger_name in (
            "org.apache.spark.util.ShutdownHookManager",
            "org.apache.spark.network.util.JavaUtils",
            "org.apache.hadoop.util.ShutdownHookManager",
        ):
            configurator.setLevel(logger_name, off)
    except Exception:  # noqa: BLE001 - silence best-effort, jamais bloquant
        pass


def read_kafka(spark: SparkSession, args: argparse.Namespace) -> DataFrame:
    starting = "earliest" if args.from_beginning else "latest"
    return (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", args.bootstrap)
        .option("subscribe", args.topic)
        .option("startingOffsets", starting)
        .option("failOnDataLoss", "false")
        .load()
    )


def main() -> int:
    args = parse_args()
    spark = build_spark()

    raw = read_kafka(spark, args)
    parsed = parse_kafka_stream(raw)
    valid, invalid = split_valid_invalid(parsed)

    # Colonnes affichées pour les événements valides
    valid_display = valid.select(
        "user_id", "video_id", "event_type", "genre", "device",
        "current_time", "duration", "event_time", "processing_time",
    )
    # Pour les invalides : on montre la raison probable + la valeur brute
    invalid_display = invalid.select(
        "kafka_partition", "kafka_offset", "raw_value", "processing_time",
    )

    trigger = {"availableNow": True} if args.once else {"processingTime": "10 seconds"}

    q_valid = (
        valid_display.writeStream.outputMode("append")
        .format("console")
        .option("truncate", "false")
        .option("numRows", 20)
        .queryName("valid-events")
        .trigger(**trigger)
        .start()
    )
    q_invalid = (
        invalid_display.writeStream.outputMode("append")
        .format("console")
        .option("truncate", "false")
        .option("numRows", 20)
        .queryName("invalid-events-dlq")
        .trigger(**trigger)
        .start()
    )

    if args.once:
        q_valid.awaitTermination()
        q_invalid.awaitTermination()
    else:
        spark.streams.awaitAnyTermination()
    return 0


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Consommateur Spark Structured Streaming")
    p.add_argument("--bootstrap", default=settings.KAFKA_BOOTSTRAP_SERVERS,
                   help="Serveurs Kafka (défaut: %(default)s)")
    p.add_argument("--topic", default=settings.KAFKA_TOPIC,
                   help="Topic source (défaut: %(default)s)")
    p.add_argument("--from-beginning", action="store_true",
                   help="Lire depuis le début du topic (startingOffsets=earliest)")
    p.add_argument("--once", action="store_true",
                   help="Traiter le backlog disponible puis s'arrêter (trigger availableNow)")
    return p.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
