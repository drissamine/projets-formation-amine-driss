#!/usr/bin/env python3
"""
Gestionnaire de Sortie SQLite pour les Résultats Spark Streaming

Gère l'enregistrement des résultats de streaming dans une base de données SQLite pour le stockage persistant
et les capacités d'interrogation.
"""

import sqlite3
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SQLiteOutputHandler:
    """Gère les opérations de sortie vers la base de données SQLite"""
    
    def __init__(self, db_path: str = "./results/streaming_results.db"):
        self.db_path = db_path
        self.conn = None
        
        # S'assurer que le répertoire existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialiser la base de données
        self._init_database()
    
    def _init_database(self):
        """Initialiser la base de données SQLite et créer les tables"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            
            # Créer les tables pour différents résultats de requête
            self._create_tables()
            
            logger.info(f"Base de données SQLite initialisée à {self.db_path}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la base SQLite: {e}")
            raise
    
    def _create_tables(self):
        """Créer les tables pour stocker les résultats de streaming"""
        cursor = self.conn.cursor()
        
        # Table pour les résultats de popularité vidéo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_popularity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                window_start TIMESTAMP,
                window_end TIMESTAMP,
                video_id TEXT,
                play_count INTEGER,
                unique_users INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table pour les résultats d'engagement utilisateur
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_engagement (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                window_start TIMESTAMP,
                window_end TIMESTAMP,
                user_id TEXT,
                session_duration REAL,
                total_watch_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table pour la détection d'inactivité
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_inactivity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                window_start TIMESTAMP,
                window_end TIMESTAMP,
                user_id TEXT,
                inactivity_minutes REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table pour les résultats d'analyse par genre
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS genre_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                window_start TIMESTAMP,
                window_end TIMESTAMP,
                genre TEXT,
                play_count INTEGER,
                unique_users INTEGER,
                avg_duration REAL,
                avg_current_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table pour la détection d'anomalies
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_time TIMESTAMP,
                alert_type TEXT,
                event_id TEXT,
                user_id TEXT,
                video_id TEXT,
                current_time REAL,
                duration REAL,
                event_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        logger.info("Tables de base de données créées avec succès")
    
    def save_video_popularity(self, window_start: datetime, window_end: datetime,
                            video_id: str, play_count: int, unique_users: int):
        """Enregistrer le résultat de popularité vidéo dans la base de données"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO video_popularity 
                (window_start, window_end, video_id, play_count, unique_users)
                VALUES (?, ?, ?, ?, ?)
            ''', (window_start, window_end, video_id, play_count, unique_users))
            
            self.conn.commit()
            logger.debug(f"Popularité vidéo enregistrée: {video_id} - {play_count} lectures")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de la popularité vidéo: {e}")
    
    def save_user_engagement(self, window_start: datetime, window_end: datetime,
                           user_id: str, session_duration: float, total_watch_time: float):
        """Enregistrer le résultat d'engagement utilisateur dans la base de données"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO user_engagement 
                (window_start, window_end, user_id, session_duration, total_watch_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (window_start, window_end, user_id, session_duration, total_watch_time))
            
            self.conn.commit()
            logger.debug(f"Engagement utilisateur enregistré: {user_id} - {session_duration} minutes")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'engagement utilisateur: {e}")
    
    def save_user_inactivity(self, window_start: datetime, window_end: datetime,
                           user_id: str, inactivity_minutes: float):
        """Enregistrer le résultat d'inactivité utilisateur dans la base de données"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO user_inactivity 
                (window_start, window_end, user_id, inactivity_minutes)
                VALUES (?, ?, ?, ?)
            ''', (window_start, window_end, user_id, inactivity_minutes))
            
            self.conn.commit()
            logger.debug(f"Inactivité utilisateur enregistrée: {user_id} - {inactivity_minutes} minutes")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'inactivité utilisateur: {e}")
    
    def save_genre_analysis(self, window_start: datetime, window_end: datetime,
                          genre: str, play_count: int, unique_users: int,
                          avg_duration: float, avg_current_time: float):
        """Enregistrer le résultat d'analyse par genre dans la base de données"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO genre_analysis 
                (window_start, window_end, genre, play_count, unique_users, avg_duration, avg_current_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (window_start, window_end, genre, play_count, unique_users, avg_duration, avg_current_time))
            
            self.conn.commit()
            logger.debug(f"Analyse par genre enregistrée: {genre} - {play_count} lectures")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'analyse par genre: {e}")
    
    def save_anomaly(self, alert_time: datetime, alert_type: str,
                   event_id: Optional[str] = None, user_id: Optional[str] = None,
                   video_id: Optional[str] = None, current_time: Optional[float] = None,
                   duration: Optional[float] = None, event_count: Optional[int] = None):
        """Enregistrer le résultat de détection d'anomalie dans la base de données"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO anomalies 
                (alert_time, alert_type, event_id, user_id, video_id, current_time, duration, event_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (alert_time, alert_type, event_id, user_id, video_id, current_time, duration, event_count))
            
            self.conn.commit()
            logger.debug(f"Anomalie enregistrée: {alert_type} pour {user_id or video_id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'anomalie: {e}")
    
    def get_latest_video_popularity(self, limit: int = 10):
        """Obtenir les derniers résultats de popularité vidéo"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT video_id, play_count, unique_users, window_start, window_end
                FROM video_popularity
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention de la popularité vidéo: {e}")
            return []
    
    def get_latest_user_engagement(self, limit: int = 10):
        """Obtenir les derniers résultats d'engagement utilisateur"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT user_id, session_duration, total_watch_time, window_start, window_end
                FROM user_engagement
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention de l'engagement utilisateur: {e}")
            return []

    def get_latest_genre_analysis(self, limit: int = 10):
        """Obtenir les derniers résultats d'analyse par genre"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT genre, play_count, unique_users, avg_duration, avg_current_time, window_start, window_end
                FROM genre_analysis
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention de l'analyse par genre: {e}")
            return []
    
    def get_latest_anomalies(self, limit: int = 20):
        """Obtenir les derniers résultats d'anomalies"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT alert_type, user_id, video_id, current_time, duration, event_count, alert_time
                FROM anomalies
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
            
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention des anomalies: {e}")
            return []
    
    def close(self):
        """Fermer la connexion à la base de données"""
        if self.conn:
            self.conn.close()
            logger.info("Connexion SQLite fermée")

def main():
    """Fonction de test pour le gestionnaire de sortie SQLite"""
    handler = SQLiteOutputHandler()
    
    # Test d'enregistrement de données
    from datetime import datetime, timedelta
    
    now = datetime.now()
    window_start = now - timedelta(minutes=10)
    window_end = now
    
    # Test popularité vidéo
    handler.save_video_popularity(window_start, window_end, "video_0001", 150, 89)
    
    # Test engagement utilisateur
    handler.save_user_engagement(window_start, window_end, "user_0001", 25.5, 450.2)
    
    # Test anomalie
    handler.save_anomaly(now, "INVALID_CURRENT_TIME", video_id="video_0002", current_time=1200.0, duration=600.0)
    
    # Test requêtes
    print("Dernière popularité vidéo:")
    for row in handler.get_latest_video_popularity():
        print(f"  {row}")
    
    print("\nDernières anomalies:")
    for row in handler.get_latest_anomalies():
        print(f"  {row}")
    
    handler.close()

if __name__ == "__main__":
    main()