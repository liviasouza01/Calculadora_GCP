"""Persistência de calculadoras compartilhadas com o cliente."""

from __future__ import annotations

import json
import os
import secrets
from pathlib import Path
from typing import Any

_DIR = Path(os.getenv("SHARES_DIR", "/tmp/calculator-shares"))
_COLLECTION = "calculator_shares"


def new_share_id() -> str:
    return secrets.token_urlsafe(18).replace("-", "").replace("_", "")[:24]


def _file_path(share_id: str) -> Path:
    _DIR.mkdir(parents=True, exist_ok=True)
    return _DIR / f"{share_id}.json"


def _firestore():
    try:
        from google.cloud import firestore

        return firestore.Client()
    except Exception:
        return None


def save_share(payload: dict[str, Any]) -> str:
    share_id = new_share_id()
    body = {"id": share_id, **payload}
    db = _firestore()
    if db is not None:
        try:
            db.collection(_COLLECTION).document(share_id).set(body)
            return share_id
        except Exception:
            pass
    _file_path(share_id).write_text(json.dumps(body), encoding="utf-8")
    return share_id


def load_share(share_id: str) -> dict[str, Any] | None:
    if not share_id or "/" in share_id or ".." in share_id:
        return None
    db = _firestore()
    if db is not None:
        try:
            snap = db.collection(_COLLECTION).document(share_id).get()
            if snap.exists:
                data = snap.to_dict() or {}
                return data
        except Exception:
            pass
    path = _file_path(share_id)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
