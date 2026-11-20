#!/usr/bin/env python3
"""
Application Spark Structured Streaming pour le Traitement d'Événements Kafka

Consomme les événements de streaming depuis le topic Kafka 'streaming-events' et effectue
une analyse en temps réel pour une plateforme de streaming vidéo.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import argparse
import logging
import os
import sys
# Ajout du chemin racine pour l'import des modules du projet
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure HADOOP_HOME/bin is in PATH for windows
if os.name == 'nt' and 'HADOOP_HOME' in os.environ:
    hadoop_bin = os.path.join(os.environ['HADOOP_HOME'], 'bin')
    if hadoop_bin not in os.environ['PATH']:
        os.environ['PATH'] += os.pathsep + hadoop_bin
        logger.info(f"Added {hadoop_bin} to PATH")
    
    # Also add to DLL search path for Python 3.8+
    try:
        os.add_dll_directory(hadoop_bin)
        logger.info(f"Added {hadoop_bin} to DLL search path")
    except (AttributeError, OSError):
        pass

class SparkStreamingProcessor:
    """Processeur principal Spark Structured Streaming"""
    
    def __init__(self, kafka_bootstrap_servers='127.0.0.1:9092', 
                 kafka_topic='streaming-events',
                 checkpoint_location='./checkpoints/spark-streaming',
                 spark_session=None):
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.kafka_topic = kafka_topic
        self.checkpoint_location = checkpoint_location
        
        # Initialiser ou injecter la session Spark
        self.spark = spark_session if spark_session else self._create_spark_session()
        
        # Définir le schéma pour les événements de streaming
        self.event_schema = self._define_schema()
    
    def _create_spark_session(self):
        """Créer et configurer la session Spark"""
        spark = SparkSession.builder \
            .appName("StreamingAnalytics") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.sql.adaptive.skewJoin.enabled", "true") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.sql.shuffle.partitions", "8") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.1") \
            .getOrCreate()
        
        # Réduire le niveau de log pour moins de verbosité
        spark.sparkContext.setLogLevel("WARN")
        
        logger.info("Session Spark créée avec succès")
        return spark
    
    def _define_schema(self):
        """Définir le schéma pour les événements de streaming"""
        return StructType([
            StructField("event_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("video_id", StringType(), True),
            StructField("event_type", StringType(), True),
            StructField("timestamp", StringType(), True),
            StructField("current_time", DoubleType(), True),
            StructField("duration", DoubleType(), True),
            StructField("genre", StringType(), True),
            StructField("device", StringType(), True)
        ])
    
    def create_streaming_dataframe(self):
        """Créer le DataFrame de streaming depuis la source Kafka"""
        try:
            # Lire depuis Kafka
            df = self.spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", self.kafka_bootstrap_servers) \
                .option("subscribe", self.kafka_topic) \
                .option("startingOffsets", "earliest") \
                .load()
            
            # Parser le JSON et appliquer le schéma
            parsed_df = df.select(
                from_json(col("value").cast("string"), self.event_schema).alias("data")
            ).select("data.*")
            
            # Ajouter le timestamp de traitement
            processed_df = parsed_df.withColumn(
                "processing_time", 
                current_timestamp()
            )
            
            # Convertir la chaîne timestamp en type timestamp
            final_df = processed_df.withColumn(
                "event_timestamp",
                to_timestamp(col("timestamp"))
            ).drop("timestamp") \
            .withWatermark("processing_time", "1 minute")
            
            logger.info("DataFrame de streaming créé avec succès")
            return final_df
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du DataFrame de streaming: {e}")
            raise
    
    def query_1_popularity(self, df):
        """Requête 1: Popularité des vidéos (top 10)"""
        # Fenêtre de 10 minutes, glissant toutes les 5 minutes
        windowed_df = df \
            .filter(col("event_type") == "PLAY") \
            .groupBy(
                window("processing_time", "10 minutes", "5 minutes"),
                "video_id"
            ) \
            .agg(
                count("*").alias("play_count"),
                approx_count_distinct("user_id").alias("unique_users")
            ) \
            .select(
                col("window.start").alias("window_start"),
                col("window.end").alias("window_end"),
                "video_id",
                "play_count",
                "unique_users"
            ) \
            .orderBy(col("window_start").desc(), col("play_count").desc())
        
        return windowed_df
    
    def query_2_engagement(self, df):
        """Requête 2: Engagement utilisateur (durée + détection inactivité >15min)"""
        # Calculer la durée de session pour chaque utilisateur
        session_df = df \
            .filter(col("event_type").isin(["PLAY", "STOP"])) \
            .groupBy(
                window("processing_time", "10 minutes", "5 minutes"),
                "user_id"
            ) \
            .agg(
                min("event_timestamp").alias("session_start"),
                max("event_timestamp").alias("session_end"),
                sum(when(col("event_type") == "PLAY", col("current_time")).otherwise(0)).alias("total_watch_time")
            ) \
            .withColumn(
                "session_duration",
                (unix_timestamp(col("session_end")) - unix_timestamp(col("session_start"))) / 60
            ) \
            .select(
                col("window.start").alias("window_start"),
                col("window.end").alias("window_end"),
                "user_id",
                "session_duration",
                "total_watch_time"
            )
        
        # Détecter l'inactivité > 15 minutes
        inactivity_df = df \
            .groupBy(
                window("processing_time", "10 minutes", "5 minutes"),
                "user_id"
            ) \
            .agg(
                max("processing_time").alias("last_activity")
            ) \
            .withColumn(
                "inactivity_minutes",
                (unix_timestamp(current_timestamp()) - unix_timestamp(col("last_activity"))) / 60
            ) \
            .filter(col("inactivity_minutes") > 15) \
            .select(
                col("window.start").alias("window_start"),
                col("window.end").alias("window_end"),
                "user_id",
                "inactivity_minutes"
            )
        
        return session_df, inactivity_df
    
    def query_3_genre_analysis(self, df):
        """Requête 3: Analyse par genre (répartition + temps moyen)"""
        genre_df = df \
            .filter(col("event_type") == "PLAY") \
            .groupBy(
                window("processing_time", "10 minutes", "5 minutes"),
                "genre"
            ) \
            .agg(
                count("*").alias("play_count"),
                approx_count_distinct("user_id").alias("unique_users"),
                avg("duration").alias("avg_duration"),
                avg("current_time").alias("avg_current_time")
            ) \
            .select(
                col("window.start").alias("window_start"),
                col("window.end").alias("window_end"),
                "genre",
                "play_count",
                "unique_users",
                round(col("avg_duration"), 2).alias("avg_duration"),
                round(col("avg_current_time"), 2).alias("avg_current_time")
            )
        
        return genre_df
    
    def query_4_anomaly_detection(self, df):
        """Requête 4: Détection d'anomalies (alertes spécifiques)"""
        # Anomalie 1: Vidéos avec current_time très élevé (potentiel corruption données)
        anomaly1_df = df \
            .filter((col("current_time") > col("duration")) | (col("current_time") < 0)) \
            .select(
                col("processing_time").alias("alert_time"),
                lit("INVALID_CURRENT_TIME").alias("alert_type"),
                "event_id",
                "user_id",
                "video_id",
                "current_time",
                "duration"
            )
        
        # Anomalie 2: Utilisateurs avec trop d'événements (potentiel activité bot)
        bot_df = df \
            .groupBy(
                window("processing_time", "10 minutes", "5 minutes"),
                "user_id"
            ) \
            .agg(count("*").alias("event_count")) \
            .filter(col("event_count") > 100) \
            .select(
                col("window.start").alias("alert_time"),
                lit("EXCESSIVE_EVENTS").alias("alert_type"),
                "user_id",
                "event_count"
            )
        
        # Anomalie 3: Vidéos avec durée zéro (potentiel problème données)
        zero_duration_df = df \
            .filter(col("duration") == 0) \
            .select(
                col("processing_time").alias("alert_time"),
                lit("ZERO_DURATION_VIDEO").alias("alert_type"),
                "event_id",
                "user_id",
                "video_id"
            )
        
        return anomaly1_df, bot_df, zero_duration_df
    
    def start_streaming(self, output_mode="update"):
        """Démarrer les requêtes de streaming vers SQLite"""
        try:
            # Créer le DataFrame de streaming
            streaming_df = self.create_streaming_dataframe()
            
            # Helper pour sauvegarder dans SQLite
            def save_q1(df, epoch_id):
                from spark.output.sqlite_output import SQLiteOutputHandler
                try:
                    handler = SQLiteOutputHandler()
                    for row in df.collect():
                        handler.save_video_popularity(
                            row['window_start'], row['window_end'], 
                            row['video_id'], row['play_count'], row['unique_users']
                        )
                    handler.close()
                except Exception as e:
                    logger.error(f"Q1 Error: {e}")

            query1 = self.query_1_popularity(streaming_df).writeStream \
                .outputMode("update") \
                .foreachBatch(save_q1) \
                .option("checkpointLocation", f"{self.checkpoint_location}/query1_db") \
                .trigger(processingTime='5 seconds') \
                .start()
            
            # Wrapper pour Query 2 - Session
            def save_q2_session(df, epoch_id):
                from spark.output.sqlite_output import SQLiteOutputHandler
                try:
                    handler = SQLiteOutputHandler()
                    for row in df.collect():
                        handler.save_user_engagement(
                            row['window_start'], row['window_end'], 
                            row['user_id'], row['session_duration'], row['total_watch_time']
                        )
                    handler.close()
                except Exception as e:
                    logger.error(f"Q2 Session Error: {e}")

            session_df, inactivity_df = self.query_2_engagement(streaming_df)
            
            query2_session = session_df.writeStream \
                .outputMode("update") \
                .foreachBatch(save_q2_session) \
                .option("checkpointLocation", f"{self.checkpoint_location}/query2_session_db") \
                .trigger(processingTime='5 seconds') \
                .start()
            
             # Wrapper pour Query 2 - Inactivity
            def save_q2_inactivity(df, epoch_id):
                from spark.output.sqlite_output import SQLiteOutputHandler
                try:
                    handler = SQLiteOutputHandler()
                    for row in df.collect():
                        handler.save_user_inactivity(
                            row['window_start'], row['window_end'], 
                            row['user_id'], row['inactivity_minutes']
                        )
                    handler.close()
                except Exception as e:
                    logger.error(f"Q2 Inactivity Error: {e}")
            
            query2_inactivity = inactivity_df.writeStream \
                .outputMode("update") \
                .foreachBatch(save_q2_inactivity) \
                .option("checkpointLocation", f"{self.checkpoint_location}/query2_inactivity_db") \
                .trigger(processingTime='5 seconds') \
                .start()

            # Wrapper pour Query 3
            def save_q3(df, epoch_id):
                from spark.output.sqlite_output import SQLiteOutputHandler
                try:
                    handler = SQLiteOutputHandler()
                    for row in df.collect():
                        handler.save_genre_analysis(
                            row['window_start'], row['window_end'], 
                            row['genre'], row['play_count'], row['unique_users'],
                            row['avg_duration'], row['avg_current_time']
                        )
                    handler.close()
                except Exception as e:
                    logger.error(f"Q3 Error: {e}")

            query3 = self.query_3_genre_analysis(streaming_df).writeStream \
                .outputMode("update") \
                .foreachBatch(save_q3) \
                .option("checkpointLocation", f"{self.checkpoint_location}/query3_db") \
                .trigger(processingTime='5 seconds') \
                .start()

            # Wrapper pour Query 4 - Anomaly
            def save_q4(df, epoch_id):
                from spark.output.sqlite_output import SQLiteOutputHandler
                try:
                    handler = SQLiteOutputHandler()
                    for row in df.collect():
                        cols = df.columns
                        kwargs = {'alert_time': row['alert_time'], 'alert_type': row['alert_type']}
                        if 'event_id' in cols: kwargs['event_id'] = row['event_id']
                        if 'user_id' in cols: kwargs['user_id'] = row['user_id']
                        if 'video_id' in cols: kwargs['video_id'] = row['video_id']
                        if 'current_time' in cols: kwargs['current_time'] = row['current_time']
                        if 'duration' in cols: kwargs['duration'] = row['duration']
                        if 'event_count' in cols: kwargs['event_count'] = row['event_count']
                        
                        handler.save_anomaly(**kwargs)
                    handler.close()
                except Exception as e:
                    logger.error(f"Q4 Error: {e}")

            anomaly1_df, bot_df, zero_duration_df = self.query_4_anomaly_detection(streaming_df)
            
            query4_anomaly1 = anomaly1_df.writeStream \
                .outputMode("update") \
                .foreachBatch(save_q4) \
                .option("checkpointLocation", f"{self.checkpoint_location}/query4_anomaly1_db") \
                .trigger(processingTime='5 seconds') \
                .start()
                
            query4_bot = bot_df.writeStream \
                .outputMode("update") \
                .foreachBatch(save_q4) \
                .option("checkpointLocation", f"{self.checkpoint_location}/query4_bot_db") \
                .trigger(processingTime='5 seconds') \
                .start()
                
            query4_zero = zero_duration_df.writeStream \
                .outputMode("update") \
                .foreachBatch(save_q4) \
                .option("checkpointLocation", f"{self.checkpoint_location}/query4_zero_db") \
                .trigger(processingTime='5 seconds') \
                .start()

            logger.info("Toutes les requêtes de streaming (SQLite) démarrées avec succès")
            
            # Attendre la terminaison de n'importe quelle requête
            self.spark.streams.awaitAnyTermination()
            
        except KeyboardInterrupt:
            logger.info("Signal d'interruption reçu, arrêt du streaming...")
        except Exception as e:
            logger.error(f"Erreur dans le streaming: {e}")
            raise
        finally:
            self.spark.stop()
            logger.info("Session Spark arrêtée")

def main():
    """Fonction principale pour exécuter l'application Spark streaming"""
    parser = argparse.ArgumentParser(description='Analyse Spark Structured Streaming')
    parser.add_argument('--kafka-bootstrap-servers', default='127.0.0.1:9092',
                       help='Serveurs bootstrap Kafka (défaut: 127.0.0.1:9092)')
    parser.add_argument('--kafka-topic', default='streaming-events',
                       help='Nom du topic Kafka (défaut: streaming-events)')
    parser.add_argument('--checkpoint-location', default='./checkpoints/spark-streaming',
                       help='Emplacement checkpoint pour Spark (défaut: ./checkpoints/spark-streaming)')
    parser.add_argument('--output-mode', default='append',
                       choices=['append', 'update', 'complete'],
                       help='Mode de sortie pour les requêtes streaming (défaut: append)')
    
    args = parser.parse_args()
    
    # Créer le processeur
    processor = SparkStreamingProcessor(
        kafka_bootstrap_servers=args.kafka_bootstrap_servers,
        kafka_topic=args.kafka_topic,
        checkpoint_location=args.checkpoint_location
    )
    
    # Démarrer le streaming
    processor.start_streaming(output_mode=args.output_mode)

if __name__ == "__main__":
    main()