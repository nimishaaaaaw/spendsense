"""
In-memory session store.

No database, no disk persistence -- per SpendSense.docx Privacy Layer:
"No raw transaction data persisted to any database. Everything processed
in-memory per session."

This is deliberately a simple dict behind a lock, keyed by a server-generated
session_id (returned to the frontend after upload, sent back on every
subsequent request). Sessions expire after SESSION_TTL_MINUTES of inactivity.

Known limitation, stated plainly: this store lives in a single process's
memory. It will NOT work correctly behind multiple backend worker processes
(e.g. `uvicorn --workers 4`) since each worker has its own memory space -- a
session created on worker A won't be visible to worker B. Fine for local dev
and single-process deployment; would need Redis or similar for multi-worker
production. Not solving that here since it's out of scope for this project's
stated goals.
"""

import threading
import uuid
from datetime import datetime, timedelta

from app.config import SESSION_TTL_MINUTES

_lock = threading.Lock()
_sessions: dict[str, dict] = {}


def create_session(data: dict) -> str:
    """
    Stores a new session's data (expects keys like 'raw_df', 'categorized_df',
    'overrides', 'subscriptions', etc. -- callers decide the shape). Returns
    the generated session_id.
    """
    session_id = str(uuid.uuid4())
    with _lock:
        _sessions[session_id] = {
            "data": data,
            "created_at": datetime.utcnow(),
            "last_accessed": datetime.utcnow(),
        }
    return session_id


def get_session(session_id: str) -> dict | None:
    """
    Returns the session's data dict, or None if the session doesn't exist
    or has expired. Touches last_accessed on successful reads (sliding TTL).
    """
    with _lock:
        _purge_expired()
        session = _sessions.get(session_id)
        if session is None:
            return None
        session["last_accessed"] = datetime.utcnow()
        return session["data"]


def update_session(session_id: str, data: dict) -> bool:
    """
    Replaces a session's data dict entirely. Returns False if session_id
    doesn't exist (caller should treat this as "session expired, re-upload").
    """
    with _lock:
        _purge_expired()
        if session_id not in _sessions:
            return False
        _sessions[session_id]["data"] = data
        _sessions[session_id]["last_accessed"] = datetime.utcnow()
        return True


def delete_session(session_id: str) -> None:
    """Explicit session deletion (e.g. user clicks 'clear my data')."""
    with _lock:
        _sessions.pop(session_id, None)


def _purge_expired() -> None:
    """
    Removes sessions past SESSION_TTL_MINUTES of inactivity. Called under
    lock from within get_session/update_session -- not exposed publicly to
    avoid double-locking.
    """
    cutoff = datetime.utcnow() - timedelta(minutes=SESSION_TTL_MINUTES)
    expired = [
        sid for sid, s in _sessions.items() if s["last_accessed"] < cutoff
    ]
    for sid in expired:
        del _sessions[sid]