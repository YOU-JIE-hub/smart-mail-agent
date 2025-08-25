import os

if os.getenv("COVERAGE_PROCESS_START"):
    try:
        import coverage  # type: ignore

        coverage.process_startup()
    except Exception:
        pass
