"""Small, side-effect free helpers."""
from __future__ import annotations
import hashlib, logging
def content_hash(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def estimate_tokens(text: str) -> int: return max(1, len(text) // 4)
def logger(name: str) -> logging.Logger: return logging.getLogger(name)
def friendly_error(exc: Exception) -> str:
    return 'The request could not be completed. Check your API key, model access, and connection, then try again.'
