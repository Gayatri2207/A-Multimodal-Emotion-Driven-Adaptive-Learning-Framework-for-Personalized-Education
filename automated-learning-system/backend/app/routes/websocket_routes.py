"""WebSocket routes for real-time emotion processing.

NOTE: The primary WebSocket handler is defined in app/main.py at /ws/emotion
and handles full multimodal fusion (facial + speech + typing).

This module is kept as a lightweight reference implementation only.
"""
# The active WebSocket handler lives in app/main.py:websocket_emotion()
# It accepts JSON payloads with optional fields:
#   - facial_frame  (base64 JPEG string)
#   - audio_chunk   (list[float] PCM at 16kHz)
#   - typing_data   { intervals: [...], mistakes: int, total_chars: int }
#   - emotion_score (float, direct override)
#   - performance_score (float, default 0.5)
#   - user_id       (int, optional)
#
# Response JSON:
#   { emotion_score, performance_score, adaptive_action, message }
