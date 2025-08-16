# Offline stub for Hugging Face transformers (minimal imports for tests).
from __future__ import annotations

__all__ = [
    "AutoTokenizer",
    "AutoModelForSequenceClassification",
    "AutoModelForSeq2SeqLM",
    "AutoConfig",
    "pipeline",
    "set_seed",
    "logging",
]


class _Dummy:
    def __call__(self, *a, **k):
        return [{"label": "unknown", "score": 0.0}]

    def __getattr__(self, name):
        return _Dummy()

    def __iter__(self):
        return iter([])


def _return_dummy(*a, **k):  # generic factory
    return _Dummy()


class AutoTokenizer:
    @classmethod
    def from_pretrained(cls, *a, **k):
        return cls()

    def __call__(self, *a, **k):
        return {}

    def encode(self, *a, **k):
        return []

    def decode(self, *a, **k):
        return ""


class _BaseModel:
    @classmethod
    def from_pretrained(cls, *a, **k):
        return cls()

    def eval(self):
        return self


class AutoModelForSequenceClassification(_BaseModel): ...


class AutoModelForSeq2SeqLM(_BaseModel): ...


class AutoConfig:
    @classmethod
    def from_pretrained(cls, *a, **k):
        return cls()


def pipeline(*a, **k):
    return _Dummy()


def set_seed(*a, **k):
    return None


class logging:
    @staticmethod
    def set_verbosity_error():
        return None
