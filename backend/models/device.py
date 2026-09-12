from __future__ import annotations

import os

import torch


def get_device() -> str:
    prefer = os.getenv("DEVICE", "").strip().lower()
    if prefer in {"cpu", "cuda", "mps"}:
        if prefer == "cuda" and not torch.cuda.is_available():
            return "cpu"
        return prefer
    return "cuda" if torch.cuda.is_available() else "cpu"

