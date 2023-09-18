from __future__ import annotations

from dataclasses import dataclass

@dataclass
class UUIDLength:
    """Simple dataclass to store UUID string lengths."""

    standard: int = 36
    hex: int = 32
