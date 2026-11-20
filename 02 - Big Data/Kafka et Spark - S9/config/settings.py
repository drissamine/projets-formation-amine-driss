"""Configuration centrale du pipeline, lue depuis les variables d'environnement (.env)."""
import os
from pathlib import Path

# Racine du projet (config/ -> parent)
BASE_DIR = Path(__file__).resolve().parent.parent


def _load_dotenv(path: Path) -> None:
    """Charge un fichier .env simple sans dépendance externe."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv(BASE_DIR / ".env")

# --- Kafka ---
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "streaming-events")
KAFKA_TOPIC_DLQ = os.environ.get("KAFKA_TOPIC_DLQ", "streaming-events-dlq")

# --- Génération d'événements ---
EVENTS_PER_SECOND = int(os.environ.get("EVENTS_PER_SECOND", "50"))
NUM_USERS = int(os.environ.get("NUM_USERS", "200"))
NUM_VIDEOS = int(os.environ.get("NUM_VIDEOS", "80"))

EVENT_TYPES = ["PLAY", "PAUSE", "STOP", "SEEK"]
GENRES = ["action", "comedy", "drama"]
DEVICES = ["mobile", "desktop", "tv"]

# --- Spark / stockage ---
# JDK pour Spark. Peut écraser un JAVA_HOME système cassé : voir ensure_java_home().
JAVA_HOME = os.environ.get("JAVA_HOME_OVERRIDE") or os.environ.get("JAVA_HOME", "")
# HADOOP_HOME (winutils.exe + hadoop.dll) requis par Spark sous Windows.
HADOOP_HOME = os.environ.get("HADOOP_HOME_OVERRIDE") or os.environ.get("HADOOP_HOME", "")
CHECKPOINT_DIR = os.environ.get("CHECKPOINT_DIR", str(BASE_DIR / "checkpoints"))
RESULTS_DIR = os.environ.get("RESULTS_DIR", str(BASE_DIR / "results"))
SQLITE_DB = os.environ.get("SQLITE_DB", str(BASE_DIR / "streaming_analytics.db"))

# --- Fenêtres glissantes (Tâche 2.2) ---
# Fenêtre de 10 minutes calculée toutes les 5 minutes (énoncé)
WINDOW_DURATION = os.environ.get("WINDOW_DURATION", "10 minutes")
SLIDE_DURATION = os.environ.get("SLIDE_DURATION", "5 minutes")
# Tolérance aux données en retard : borne l'état conservé par Spark
WATERMARK_DELAY = os.environ.get("WATERMARK_DELAY", "15 minutes")

# Détection d'inactivité : utilisateur sans événement depuis > N minutes
INACTIVITY_THRESHOLD_MIN = int(os.environ.get("INACTIVITY_THRESHOLD_MIN", "15"))

# Détection d'anomalies
ANOMALY_USER_VIDEOS_THRESHOLD = int(os.environ.get("ANOMALY_USER_VIDEOS_THRESHOLD", "10"))
ANOMALY_USER_WINDOW = os.environ.get("ANOMALY_USER_WINDOW", "1 hour")
ANOMALY_USER_SLIDE = os.environ.get("ANOMALY_USER_SLIDE", "10 minutes")
ANOMALY_DEVICE_THRESHOLD = int(os.environ.get("ANOMALY_DEVICE_THRESHOLD", "1000"))
ANOMALY_DEVICE_WINDOW = os.environ.get("ANOMALY_DEVICE_WINDOW", "5 minutes")  # tumbling


def ensure_java_home() -> None:
    """Force JAVA_HOME sur le JDK du projet avant de lancer Spark.

    Écrase un JAVA_HOME système éventuellement cassé (cf. JDK temporaire incomplet).
    """
    if JAVA_HOME:
        os.environ["JAVA_HOME"] = JAVA_HOME
        bin_dir = str(Path(JAVA_HOME) / "bin")
        if bin_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")


def ensure_hadoop_home() -> None:
    """Force HADOOP_HOME (winutils.exe + hadoop.dll) avant de lancer Spark sous Windows."""
    if HADOOP_HOME:
        os.environ["HADOOP_HOME"] = HADOOP_HOME
        bin_dir = str(Path(HADOOP_HOME) / "bin")
        if bin_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")


def checkpoint_path(name: str) -> str:
    """Dossier de checkpoint dédié à une requête (créé si besoin). Reprise sur incident."""
    path = Path(CHECKPOINT_DIR) / name
    path.mkdir(parents=True, exist_ok=True)
    return str(path)
