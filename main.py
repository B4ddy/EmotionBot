import threading
from UI import SpeechLogApp
from AI import AIProcessor
from audio import AudioEngine

def main():
    # KI-Modelle initialisieren (kann auf Raspberry Pi 5 bis zu 30 Sekunden dauern)
    ai_proc = AIProcessor()
    
    # Benutzeroberfläche initialisieren
    app = SpeechLogApp()

    # Callback-Funktionen für Audio Engine
    def on_speech():
        app.show_listening()

    def on_proc():
        app.show_thinking()

    def on_trans(text, emotion):
        print(f"Processed Speech: {text}")
        print(f"Processed Emotion: {emotion}")
        app.show_emotion(emotion)

    # Audio Engine konfigurieren
    engine = AudioEngine(
        on_speech_start=on_speech,
        on_processing=on_proc,
        on_transcription=on_trans
    )

    # Audio-Thread starten (läuft parallel zur GUI)
    audio_thread = threading.Thread(
        target=engine.start_listening,
        args=(ai_proc,),
        daemon=True
    )
    audio_thread.start()

    # GUI starten (blockiert bis Fenster geschlossen wird)
    app.run()

if __name__ == '__main__':
    main()
