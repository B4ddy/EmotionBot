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
        self.actual_rate = RATE

    def _find_working_audio_config(self, p):
        """Find a working audio configuration by testing different sample rates."""
        # WebRTC VAD only supports 8000, 16000, 32000, 48000 Hz
        supported_rates = [16000, 48000, 32000, 8000]
        
        for rate in supported_rates:
            try:
                # Try to open stream with this rate
                test_stream = p.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=rate,
                    input=True,
                    frames_per_buffer=int(rate * 30 / 1000)  # 30ms chunks
                )
                test_stream.close()
                print(f"[AudioEngine] Using sample rate: {rate} Hz")
                return rate, int(rate * 30 / 1000)
            except Exception as e:
                print(f"[AudioEngine] Sample rate {rate} Hz not supported: {e}")
                continue
        
        raise RuntimeError("No supported audio configuration found. Please check your audio device.")

    def start_listening(self, ai_processor):
        p = pyaudio.PyAudio()
        
        # audio devices für debug
        print("\n[AudioEngine] Available audio devices:")
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"  Device {i}: {info['name']} (Sample Rate: {info['defaultSampleRate']})")
        
        # Find working audio config
        try:
            self.actual_rate, chunk_size = self._find_working_audio_config(p)
        except RuntimeError as e:
            print(f"[AudioEngine] Error: {e}")
            p.terminate()
            return
        
        # Audio-Stream öffnen (auf Raspberry Pi USB-Mikrofon oder Audio-HAT erforderlich)
        try:
            stream = p.open(format=FORMAT, channels=CHANNELS, rate=self.actual_rate,
                            input=True, frames_per_buffer=chunk_size)
        except Exception as e:
            print(f"[AudioEngine] Failed to open audio stream: {e}")
            p.terminate()
            return

        frames = deque()
        is_recording = False
        silence_start_time = None

        try:
            while self.is_running:
                try:
                    chunk = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                except OSError: continue  # Buffer-Overflow ignorieren

                # Voice Activity Detection (VAD) prüft ob Sprache erkannt wird
                if self.vad.is_speech(chunk, self.actual_rate):
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
                        results = ai_processor.transcribe(list(frames), self.actual_rate)
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