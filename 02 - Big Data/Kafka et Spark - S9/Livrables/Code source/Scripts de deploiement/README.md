# Scripts de déploiement

> **Auteur : DRISS Amine**  —  ESIS 2 (2025-2026)


Infrastructure, dépendances et tests de charge.

## Fichiers

| Fichier | Rôle |
|---|---|
| `docker-compose.yml` | Kafka 3.7 (mode KRaft) + Kafka UI, listener `localhost:29092`. |
| `requirements.txt` | Dépendances Python (kafka-python, pyspark). |
| `.env.example` | Modèle de configuration à copier en `.env`. |
| `setup.ps1` | Déploiement tout-en-un (Windows/PowerShell) : Docker → topics → dépendances Python. |
| `create_topic.ps1` | Création des topics Kafka (Windows). |
| `create_topic.sh` | Création des topics Kafka (Linux/macOS). |
| `load_test.py` | Test de charge et d'évolutivité (10K / 50K / 100K événements). |
| `crash_recovery_test.py` | Test de crash + reprise sur checkpoint (30K événements). |
| `render_terminal.py` | Utilitaire : rendu d'un texte en PNG façon terminal (pour screenshots). |

## Démarrage rapide

```powershell
# Windows / PowerShell
pwsh scripts/setup.ps1
```

```bash
# Linux / macOS
docker compose up -d
bash scripts/create_topic.sh
pip install -r requirements.txt
```

## Configuration

Copier `.env.example` en `.env` et adapter :

- `KAFKA_BOOTSTRAP_SERVERS` (défaut `localhost:29092`)
- `JAVA_HOME_OVERRIDE` (chemin du JDK 17, requis par Spark)
- `HADOOP_HOME_OVERRIDE` (chemin contenant `bin/winutils.exe` + `bin/hadoop.dll`,
  requis par Spark **sous Windows uniquement**)
- `CHECKPOINT_DIR` (chemin **sans espaces** — Hadoop gère mal les espaces)

## Tests de charge et de crash

```bash
# Test d'évolutivité (10K, 50K, 100K)
python -m scripts.load_test

# Test de crash + reprise
python -m scripts.crash_recovery_test
```