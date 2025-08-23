from importlib import import_module as _im
_m = _im("smart_mail_agent.ingestion.email_processor")
extract_fields = getattr(_m, "extract_fields", lambda *_a, **_k: ({}, []))
write_classification_result = getattr(_m, "write_classification_result", lambda *_a, **_k: None)
__all__ = ["extract_fields", "write_classification_result"]
