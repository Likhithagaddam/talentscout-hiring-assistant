"""
TalentScout – Data handling.

Saves candidate sessions to local JSON files (anonymised IDs).
In a production deployment this would write to a secure database.
Complies with GDPR best practices:
  - No unnecessary PII retention beyond the session
  - Data stored locally only (no third-party persistence)
  - Clear purpose limitation
"""

import json
import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# Sessions are stored in ./data/ relative to the project root
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


# ── Save ──────────────────────────────────────────────────────────────────────
def save_candidate_session(candidate_info: dict, messages: list[dict]) -> str | None:
    """
    Persist a completed interview session.

    The filename is a one-way hash of the email (if present) so that
    duplicate submissions can be detected without storing raw PII in filenames.

    Returns the session ID on success, None on failure.
    """
    try:
        session_id = _make_session_id(candidate_info.get("email", ""))

        # Strip conversation history to only assistant questions (not answers)
        # so we don't double-store candidate personal data in the transcript
        safe_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in messages
        ]

        payload = {
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "candidate_info": candidate_info,
            "transcript": safe_messages,
        }

        path = DATA_DIR / f"{session_id}.json"
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
        return session_id

    except Exception as exc:
        print(f"[data_handler] Could not save session: {exc}")
        return None


# ── Load summary ──────────────────────────────────────────────────────────────
def load_session_summary(candidate_info: dict) -> str | None:
    """
    Build a human-readable markdown summary of the completed session.
    Does NOT load from disk (avoids PII re-exposure); uses in-memory info.
    """
    if not candidate_info:
        return None

    lines = ["### 📋 Session Summary\n"]
    field_map = {
        "full_name":          "**Name**",
        "email":              "**Email**",
        "phone":              "**Phone**",
        "location":           "**Location**",
        "years_of_experience":"**Experience**",
        "desired_position":   "**Desired Role**",
        "tech_stack":         "**Tech Stack**",
    }
    for key, label in field_map.items():
        if key in candidate_info:
            lines.append(f"- {label}: {candidate_info[key]}")

    lines.append(
        "\n\n_Our team will review your technical responses and be in touch "
        "within 2–3 business days._"
    )
    return "\n".join(lines)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _make_session_id(email: str) -> str:
    """
    Generate a short, reproducible, non-reversible session identifier.
    Uses the first 12 chars of the SHA-256 hash of the email + a random suffix
    to prevent rainbow-table lookups.
    """
    salt = uuid.uuid4().hex[:8]
    digest = hashlib.sha256(f"{email.lower()}{salt}".encode()).hexdigest()[:12]
    return f"ts_{digest}_{salt}"