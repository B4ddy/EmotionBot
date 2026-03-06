import pyaudio
import os

# Audio-Konfiguration
FORMAT = pyaudio.paInt16  # 16-bit Audio
CHANNELS = 1  # Mono
RATE = 16000  # 16kHz Sample-Rate (Standard für Whisper)
CHUNK_DURATION_MS = 30  # 30ms Chunks (erforderlich für WebRTC VAD)
CHUNK_SIZE = int(RATE * CHUNK_DURATION_MS / 1000)
VAD_AGGRESSIVENESS = 3  # Höchste Stufe (0-3), filtert Hintergrundgeräusche aggressiv
SILENCE_DURATION_MS = 1000  # 1 Sekunde Stille beendet Aufnahme


# KI-Modell-Konfiguration
# Whisper Modellgrößen: tiny, base, small, medium, large
# Für Raspberry Pi 5: "small" empfohlen (Balance zwischen Genauigkeit und Geschwindigkeit)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"Base directory: {BASE_DIR}")

WHISPER_MODEL_SIZE = "small"  # ~500MB RAM, ~5-10s Inferenzzeit auf RPi 5
EMOTION_MODEL_NAME = os.path.join(BASE_DIR, "models", "emotion_classifier")  # Lokales Modell (tsid7710/distillbert-emotion-model)