"""Investigation progress tracking (Redis with in-memory fallback)."""

import json
import logging
import os
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Phase weights for overall percent (must sum to 100)
PHASE_WEIGHTS = {
    "queued": (0, 5),
    "static_analysis": (5, 45),
    "dynamic_analysis": (45, 65),
    "risk_scoring": (65, 75),
    "ai_reasoning": (75, 90),
    "persisting": (90, 98),
    "completed": (100, 100),
}

# Estimated seconds per phase (for ETA)
PHASE_ETA_SECONDS = {
    "queued": 5,
    "static_analysis": 90,
    "dynamic_analysis": 120,
    "risk_scoring": 10,
    "ai_reasoning": 45,
    "persisting": 15,
    "completed": 0,
}

_memory: Dict[str, Dict[str, Any]] = {}


def _redis_client():
    try:
        import redis

        url = os.getenv("REDIS_URL")
        if not url:
            return None
        return redis.from_url(url, decode_responses=True)
    except Exception as e:
        logger.debug(f"Redis unavailable for progress: {e}")
        return None


def set_progress(apk_id: str, phase: str, message: str, phase_percent: int = 0) -> None:
    """Update investigation progress for an APK."""
    start = _memory.get(apk_id, {}).get("started_at")
    if not start:
        start = time.time()

    low, high = PHASE_WEIGHTS.get(phase, (0, 100))
    span = max(high - low, 1)
    overall = min(99, low + int(span * (phase_percent / 100))) if phase != "completed" else 100

    remaining_phases = list(PHASE_WEIGHTS.keys())
    try:
        idx = remaining_phases.index(phase)
        eta = sum(PHASE_ETA_SECONDS.get(p, 30) for p in remaining_phases[idx:])
        eta = int(eta * (1 - overall / 100))
    except ValueError:
        eta = 120

    payload = {
        "apk_id": apk_id,
        "phase": phase,
        "message": message,
        "percent": overall,
        "phase_percent": phase_percent,
        "eta_seconds": max(eta, 0),
        "started_at": start,
        "updated_at": time.time(),
    }

    _memory[apk_id] = payload

    client = _redis_client()
    if client:
        try:
            client.setex(f"investigation:progress:{apk_id}", 3600, json.dumps(payload))
        except Exception as e:
            logger.warning(f"Failed to write progress to Redis: {e}")


def get_progress(apk_id: str) -> Optional[Dict[str, Any]]:
    client = _redis_client()
    if client:
        try:
            raw = client.get(f"investigation:progress:{apk_id}")
            if raw:
                return json.loads(raw)
        except Exception:
            pass
    return _memory.get(apk_id)


def clear_progress(apk_id: str) -> None:
    _memory.pop(apk_id, None)
    client = _redis_client()
    if client:
        try:
            client.delete(f"investigation:progress:{apk_id}")
        except Exception:
            pass
