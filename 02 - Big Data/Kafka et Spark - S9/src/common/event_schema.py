"""Schéma et génération des événements de streaming (Tâche 1.1).

Schéma d'un événement :
    {
      "event_id":    "uuid",
      "user_id":     "user_0042",
      "video_id":    "video_017",
      "event_type":  "PLAY|PAUSE|STOP|SEEK",
      "timestamp":   "2026-06-27T12:34:56.789+00:00",  (ISO 8601)
      "current_time": 123.45,   (position de lecture en secondes)
      "duration":     600.00,   (durée totale de la vidéo en secondes)
      "genre":        "action|comedy|drama",
      "device":       "mobile|desktop|tv"
    }
"""
from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone

from config import settings


class EventGenerator:
    """Génère des événements cohérents : chaque vidéo garde un genre et une durée fixes."""

    def __init__(self, num_users: int | None = None, num_videos: int | None = None, seed: int | None = None):
        self.rng = random.Random(seed)
        self.num_users = num_users or settings.NUM_USERS
        self.num_videos = num_videos or settings.NUM_VIDEOS

        # Catalogue vidéo : genre + durée stables par video_id
        self.videos = {
            f"video_{i:03d}": {
                "genre": self.rng.choice(settings.GENRES),
                "duration": round(self.rng.uniform(120.0, 7200.0), 2),
            }
            for i in range(self.num_videos)
        }
        self.video_ids = list(self.videos.keys())
        self.user_ids = [f"user_{i:04d}" for i in range(self.num_users)]

    def generate(self) -> dict:
        """Construit un événement valide aléatoire."""
        video_id = self.rng.choice(self.video_ids)
        video = self.videos[video_id]
        duration = video["duration"]

        return {
            "event_id": str(uuid.uuid4()),
            "user_id": self.rng.choice(self.user_ids),
            "video_id": video_id,
            "event_type": self.rng.choice(settings.EVENT_TYPES),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "current_time": round(self.rng.uniform(0.0, duration), 2),
            "duration": duration,
            "genre": video["genre"],
            "device": self.rng.choice(settings.DEVICES),
        }
