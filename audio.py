import pyaudio
import webrtcvad
import time
from collections import deque
from config import FORMAT, CHANNELS, RATE, CHUNK_SIZE, VAD_AGGRESSIVENESS, SILENCE_DURATION_MS

class AudioEngine:
    def __init__(self, on_speech_start=None, on_processing=None, on_transcription=None):
        self.vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
        self.on_speech_start = on_speech_start
        self.on_processing = on_processing
        self.on_transcription = on_transcription
        self.is_running = True

    def start_listening(self, ai_processor):
        p = pyaudio.PyAudio()
        # Audio-Stream öffnen (auf Raspberry Pi USB-Mikrofon oder Audio-HAT erforderlich)
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, frames_per_buffer=CHUNK_SIZE)

        frames = deque()
        is_recording = False
        silence_start_time = None

        try:
            while self.is_running:
                try:
                    chunk = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                except OSError: continue  # Buffer-Overflow ignorieren

                # Voice Activity Detection (VAD) prüft ob Sprache erkannt wird
                if self.vad.is_speech(chunk, RATE):
                    if not is_recording:
                        if self.on_speech_start: self.on_speech_start()
                        is_recording = True
                    frames.append(chunk)
                    silence_start_time = None
                elif is_recording:
                    frames.append(chunk)
                    if silence_start_time is None:
                        silence_start_time = time.time()
                    elif (time.time() - silence_start_time) * 1000 > SILENCE_DURATION_MS:
                        if self.on_processing: self.on_processing()
                        
                        # Transkription durchführen
                        results = ai_processor.transcribe(list(frames))
                        if self.on_transcription:
                            for res in results:
                                self.on_transcription(res['text'], res['emotion'])
                        
                        frames.clear()
                        is_recording = False
                        silence_start_time = None
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()