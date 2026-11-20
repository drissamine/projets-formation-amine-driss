# Spark Output Handlers

## Description
Gestion des sorties des résultats Spark Streaming vers différents formats et destinations.

## Composants

### SQLite Output Handler (`sqlite_output.py`)
- **Objectif**: Stockage persistant des résultats dans une base de données SQLite
- **Tables**: 5 tables pour les différents types de résultats
- **Fonctionnalités**:
  - Sauvegarde des résultats en temps réel
  - Requêtes pour consultation des données historiques
  - Gestion des connexions et fermeture propre

### File Output Handler (`file_output.py`)
- **Objectif**: Sauvegarde des résultats dans des fichiers JSON et CSV
- **Formats**: JSON (structuré) et CSV (pour analyse externe)
- **Fonctionnalités**:
  - Timestamps automatiques dans les noms de fichiers
  - Organisation par type de sortie (json/, csv/)
  - Nettoyage automatique des anciens fichiers
  - Statistiques sur les fichiers générés

## Architecture des Sorties

### Console Output (déjà implémenté dans `spark_streaming_app.py`)
- **Format**: Affichage en temps réel dans la console
- **Fréquence**: Mise à jour toutes les 30 secondes
- **Utilisation**: Monitoring et débogage

### File Output
```
results/
├── json/
│   ├── video_popularity_20240101_100000.json
│   ├── user_engagement_20240101_100000.json
│   ├── genre_analysis_20240101_100000.json
│   └── anomalies_20240101_100000.json
└── csv/
    ├── video_popularity_20240101_100000.csv
    ├── user_engagement_20240101_100000.csv
    ├── genre_analysis_20240101_100000.csv
    └── anomalies_20240101_100000.csv
```

### SQLite Database
```
streaming_results.db
├── video_popularity (table)
├── user_engagement (table)
├── user_inactivity (table)
├── genre_analysis (table)
└── anomalies (table)
```

## Intégration avec Spark Streaming

### Modification de `spark_streaming_app.py`
Pour intégrer les output handlers, il faut modifier les méthodes de streaming:

```python
# Dans la classe SparkStreamingProcessor
def __init__(self, ...):
    # ... existing code ...
    self.sqlite_handler = SQLiteOutputHandler()
    self.file_handler = FileOutputHandler()

def start_streaming(self, output_mode="append"):
    # ... existing code ...
    
    # Query 1 with file output
    query1_file = query1_df \
        .writeStream \
        .outputMode(output_mode) \
        .foreachBatch(self.process_video_popularity_batch) \
        .option("checkpointLocation", f"{self.checkpoint_location}/query1_file") \
        .trigger(processingTime='30 seconds') \
        .start()

def process_video_popularity_batch(self, batch_df, batch_id):
    """Process batch for video popularity"""
    # Convert to list of dicts
    results = batch_df.collect()
    
    # Save to file
    self.file_handler.save_video_popularity(results)
    
    # Save to SQLite
    for row in results:
        self.sqlite_handler.save_video_popularity(
            row.window_start, row.window_end, 
            row.video_id, row.play_count, row.unique_users
        )
```

## Formats de Données

### Video Popularity
```json
{
  "window_start": "2024-01-01T10:00:00",
  "window_end": "2024-01-01T10:10:00",
  "video_id": "video_0001",
  "play_count": 150,
  "unique_users": 89
}
```

### User Engagement
```json
{
  "window_start": "2024-01-01T10:00:00",
  "window_end": "2024-01-01T10:10:00",
  "user_id": "user_0001",
  "session_duration": 25.5,
  "total_watch_time": 450.2
}
```

### User Inactivity
```json
{
  "window_start": "2024-01-01T10:00:00",
  "window_end": "2024-01-01T10:10:00",
  "user_id": "user_0002",
  "inactivity_minutes": 18.5
}
```

### Genre Analysis
```json
{
  "window_start": "2024-01-01T10:00:00",
  "window_end": "2024-01-01T10:10:00",
  "genre": "action",
  "play_count": 200,
  "unique_users": 150,
  "avg_duration": 1200.5,
  "avg_current_time": 650.2
}
```

### Anomalies
```json
{
  "alert_time": "2024-01-01T10:05:00",
  "alert_type": "INVALID_CURRENT_TIME",
  "event_id": "evt_12345",
  "user_id": "user_0003",
  "video_id": "video_0004",
  "current_time": 1200.0,
  "duration": 600.0,
  "event_count": null
}
```

## Configuration

### SQLite Database
- **Emplacement**: `./results/streaming_results.db`
- **Tables**: 5 tables pour chaque type de résultat
- **Index**: Création automatique des indexes pour les performances

### File Output
- **Répertoire**: `./results/`
- **Sous-répertoires**: `json/` et `csv/`
- **Nettoyage**: Fichiers plus vieux que 7 jours sont supprimés

## Monitoring et Statistiques

### File Output Stats
```python
handler = FileOutputHandler()
stats = handler.get_output_stats()
print(stats)
# Output:
# {
#   'json_files': 15,
#   'csv_files': 15,
#   'total_size_mb': 2.5,
#   'latest_files': {
#     'video_popularity': 'video_popularity_20240101_100000.json',
#     'anomalies': 'anomalies_20240101_100000.json'
#   }
# }
```

### SQLite Queries
```python
handler = SQLiteOutputHandler()
# Get latest video popularity
results = handler.get_latest_video_popularity(limit=10)

# Get latest anomalies
anomalies = handler.get_latest_anomalies(limit=20)
```

## Performance

### File Output Optimization
- **Batch processing**: Écriture par lots pour réduire les opérations I/O
- **Compression**: Option de compression des fichiers JSON
- **Rotation**: Rotation automatique des fichiers pour éviter les fichiers trop gros

### SQLite Optimization
- **Transactions**: Utilisation de transactions pour les insertions par lots
- **Indexes**: Index sur les colonnes fréquemment consultées
- **Connection pooling**: Gestion efficace des connexions

## Dépannage

### Problèmes courants

#### Erreur d'écriture de fichiers
```bash
# Vérifier les permissions du répertoire
ls -la ./results/

# Vérifier l'espace disque
df -h .
```

#### Erreur SQLite
```bash
# Vérifier que le fichier de base de données est accessible
ls -la ./results/streaming_results.db

# Tester la connexion
sqlite3 ./results/streaming_results.db ".tables"
```

#### Problèmes de mémoire
```bash
# Augmenter la mémoire allouée à Spark
export SPARK_DRIVER_MEMORY=2g
export SPARK_EXECUTOR_MEMORY=4g
```

## Intégration

### Avec Spark Streaming
Les output handlers sont conçus pour être intégrés dans le pipeline Spark Streaming existant:

1. **Console output**: Déjà implémenté pour le monitoring
2. **File output**: Ajout via `foreachBatch` pour une sauvegarde persistante
3. **SQLite output**: Ajout via `foreachBatch` pour une consultation structurée

### Avec d'autres systèmes
Les fichiers JSON/CSV générés peuvent être facilement intégrés avec:
- **Power BI/Tableau**: Pour la visualisation
- **ELK Stack**: Pour l'analyse et le monitoring
- **Data Lakes**: Pour le stockage à long terme