import torch
import numpy as np
from faster_whisper import WhisperModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from config import WHISPER_MODEL_SIZE, EMOTION_MODEL_NAME

class AIProcessor:
    def __init__(self):
        print("Loading Whisper...")
        # CPU-Modus mit int8 für Raspberry Pi optimiert (reduziert RAM-Verbrauch)
        self.whisper = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
        
        print("Loading Emotion Model...")
        self.tokenizer = AutoTokenizer.from_pretrained(EMOTION_MODEL_NAME)
        self.emotion_model = AutoModelForSequenceClassification.from_pretrained(EMOTION_MODEL_NAME)
        self.emotions = ["sad", "joy", "love", "anger", "fear", "surprise"]

    def detect_emotion(self, text):
        inputs = self.tokenizer(text, return_tensors="pt")
        with torch.inference_mode():
            logits = self.emotion_model(**inputs).logits
        prediction = torch.argmax(logits, dim=-1).item()
        return self.emotions[prediction]

    def transcribe(self, frames, sample_rate=16000):
        audio_data = b"".join(frames)
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Resample if necessary - Whisper expects 16kHz
        if sample_rate != 16000:
            # Simple resampling using numpy interpolation
            duration = len(audio_array) / sample_rate
            target_length = int(duration * 16000)
            audio_array = np.interp(
                np.linspace(0, len(audio_array), target_length),
                np.arange(len(audio_array)),
                audio_array
            )
        
        # beam_size=1 für schnellere Inferenz auf Raspberry Pi (Greedy Decoding)
        segments, _ = self.whisper.transcribe(audio_array, language="en", beam_size=1)
        results = []
        for segment in segments:
            emotion = self.detect_emotion(segment.text)
            results.append({"text": segment.text, "emotion": emotion})
        return results