"""Application logging configuration."""

import logging
import sys


def _make_utf8_stream(stream):
    """Wrap a stream in a UTF-8 TextIOWrapper so Unicode chars (✓, etc.) work on Windows."""
    try:
        import io
        if hasattr(stream, "buffer"):
            return io.TextIOWrapper(stream.buffer, encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass
    return stream


# Create logger for application
logger = logging.getLogger("emotion_adaptive_learning")

# Only configure if not already configured
if not logger.handlers:
    logger.setLevel(logging.INFO)

    # Use UTF-8 aware stream to avoid UnicodeEncodeError on Windows (cp1252)
    utf8_stream = _make_utf8_stream(sys.stdout)
    handler = logging.StreamHandler(utf8_stream)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Prevent propagation to avoid duplicate logs
logger.propagate = False
