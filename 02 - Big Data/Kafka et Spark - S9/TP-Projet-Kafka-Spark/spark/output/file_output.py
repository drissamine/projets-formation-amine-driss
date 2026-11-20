#!/usr/bin/env python3
"""
Gestionnaire de Sortie Fichiers pour les Résultats Spark Streaming

Gère l'enregistrement des résultats de streaming dans différents formats de fichiers (JSON, CSV)
pour le stockage persistant et des analyses ultérieures.
"""

import json
import csv
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import os
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FileOutputHandler:
    """Gère les opérations de sortie vers les fichiers (JSON, CSV)"""
    
    def __init__(self, output_dir: str = "./results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sous-répertoires pour différents types de sortie
        self.json_dir = self.output_dir / "json"
        self.csv_dir = self.output_dir / "csv"
        self.json_dir.mkdir(exist_ok=True)
        self.csv_dir.mkdir(exist_ok=True)
    
    def save_json(self, data: List[Dict[str, Any]], filename_prefix: str):
        """Enregistrer les données dans un fichier JSON avec horodatage"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.json"
            filepath = self.json_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"{len(data)} enregistrements enregistrés dans {filepath}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du fichier JSON: {e}")
    
    def save_csv(self, data: List[Dict[str, Any]], filename_prefix: str, 
                 fieldnames: Optional[List[str]] = None):
        """Enregistrer les données dans un fichier CSV avec horodatage"""
        try:
            if not data:
                logger.warning("Aucune donnée à enregistrer dans le CSV")
                return
            
            # Utiliser les noms de champs fournis, sinon les extraire du premier enregistrement
            if not fieldnames:
                fieldnames = list(data[0].keys())
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename_prefix}_{timestamp}.csv"
            filepath = self.csv_dir / filename
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"{len(data)} enregistrements enregistrés dans {filepath}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du fichier CSV: {e}")
    
    def save_video_popularity(self, results: List[Dict[str, Any]]):
        """Enregistrer les résultats de popularité vidéo"""
        self.save_json(results, "video_popularity")
        
        # Enregistrer également en CSV avec champs spécifiques
        csv_fields = ['window_start', 'window_end', 'video_id', 'play_count', 'unique_users']
        self.save_csv(results, "video_popularity", csv_fields)
    
    def save_user_engagement(self, results: List[Dict[str, Any]]):
        """Enregistrer les résultats d'engagement utilisateur"""
        self.save_json(results, "user_engagement")
        
        # Enregistrer également en CSV avec champs spécifiques
        csv_fields = ['window_start', 'window_end', 'user_id', 'session_duration', 'total_watch_time']
        self.save_csv(results, "user_engagement", csv_fields)
    
    def save_user_inactivity(self, results: List[Dict[str, Any]]):
        """Enregistrer les résultats d'inactivité utilisateur"""
        self.save_json(results, "user_inactivity")
        
        # Enregistrer également en CSV avec champs spécifiques
        csv_fields = ['window_start', 'window_end', 'user_id', 'inactivity_minutes']
        self.save_csv(results, "user_inactivity", csv_fields)
    
    def save_genre_analysis(self, results: List[Dict[str, Any]]):
        """Enregistrer les résultats d'analyse par genre"""
        self.save_json(results, "genre_analysis")
        
        # Enregistrer également en CSV avec champs spécifiques
        csv_fields = ['window_start', 'window_end', 'genre', 'play_count', 'unique_users', 
                     'avg_duration', 'avg_current_time']
        self.save_csv(results, "genre_analysis", csv_fields)
    
    def save_anomalies(self, results: List[Dict[str, Any]]):
        """Enregistrer les résultats de détection d'anomalies"""
        self.save_json(results, "anomalies")
        
        # Enregistrer également en CSV avec champs spécifiques
        csv_fields = ['alert_time', 'alert_type', 'event_id', 'user_id', 'video_id', 
                     'current_time', 'duration', 'event_count']
        self.save_csv(results, "anomalies", csv_fields)
    
    def get_latest_files(self, file_type: str, limit: int = 5) -> List[Path]:
        """Obtenir la liste des fichiers les plus récents pour un type spécifique"""
        try:
            search_pattern = f"{file_type}_*.json"
            files = list(self.json_dir.glob(search_pattern))
            
            # Trier par heure de modification (plus récent en premier)
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            return files[:limit]
            
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention des fichiers récents: {e}")
            return []
    
    def read_json_file(self, filepath: Path) -> List[Dict[str, Any]]:
        """Lire les données depuis un fichier JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
            
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier JSON {filepath}: {e}")
            return []
    
    def cleanup_old_files(self, days_to_keep: int = 7):
        """Supprimer les fichiers plus anciens que le nombre de jours spécifié"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
            
            # Nettoyer les fichiers JSON
            for filepath in self.json_dir.glob("*.json"):
                if filepath.stat().st_mtime < cutoff_time:
                    filepath.unlink()
                    logger.info(f"Fichier ancien supprimé: {filepath}")
            
            # Nettoyer les fichiers CSV
            for filepath in self.csv_dir.glob("*.csv"):
                if filepath.stat().st_mtime < cutoff_time:
                    filepath.unlink()
                    logger.info(f"Fichier ancien supprimé: {filepath}")
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des fichiers anciens: {e}")
    
    def get_output_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques sur les fichiers de sortie"""
        try:
            stats = {
                'json_files': len(list(self.json_dir.glob("*.json"))),
                'csv_files': len(list(self.csv_dir.glob("*.csv"))),
                'total_size_mb': 0,
                'latest_files': {}
            }
            
            # Calculer la taille totale
            total_size = 0
            for filepath in self.json_dir.glob("*.json"):
                total_size += filepath.stat().st_size
            for filepath in self.csv_dir.glob("*.csv"):
                total_size += filepath.stat().st_size
            
            stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            
            # Obtenir les fichiers les plus récents par type
            file_types = ['video_popularity', 'user_engagement', 'user_inactivity', 
                         'genre_analysis', 'anomalies']
            
            for file_type in file_types:
                latest_files = self.get_latest_files(file_type, 1)
                if latest_files:
                    stats['latest_files'][file_type] = str(latest_files[0])
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention des statistiques de sortie: {e}")
            return {}

def main():
    """Fonction de test pour le gestionnaire de sortie fichiers"""
    handler = FileOutputHandler()
    
    # Données de test
    test_video_popularity = [
        {
            'window_start': '2024-01-01 10:00:00',
            'window_end': '2024-01-01 10:10:00',
            'video_id': 'video_0001',
            'play_count': 150,
            'unique_users': 89
        },
        {
            'window_start': '2024-01-01 10:00:00',
            'window_end': '2024-01-01 10:10:00',
            'video_id': 'video_0002',
            'play_count': 120,
            'unique_users': 75
        }
    ]
    
    test_anomalies = [
        {
            'alert_time': '2024-01-01 10:05:00',
            'alert_type': 'INVALID_CURRENT_TIME',
            'video_id': 'video_0003',
            'current_time': 1200.0,
            'duration': 600.0
        }
    ]
    
    # Enregistrer les données de test
    handler.save_video_popularity(test_video_popularity)
    handler.save_anomalies(test_anomalies)
    
    # Obtenir les statistiques
    stats = handler.get_output_stats()
    print("Statistiques de sortie:", stats)
    
    # Obtenir les fichiers les plus récents
    latest_files = handler.get_latest_files('video_popularity')
    print("Derniers fichiers de popularité vidéo:", [str(f) for f in latest_files])

if __name__ == "__main__":
    main()