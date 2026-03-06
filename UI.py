from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import mainthread, Clock
from Emojis.emoji_paths import EMOJI_PATHS
import os

class SpeechLogApp(App):
    def build(self):
        self.emoji_image = Image(source=EMOJI_PATHS["default"][0])
        self.current_emotion = None
        self.emotion_index = 0
        self.animation_event = None
        return self.emoji_image

    @mainthread
    def show_default(self):
        self.stop_animation()
        self.emoji_image.source = EMOJI_PATHS["default"][0]
        self.emoji_image.reload()

    @mainthread
    def show_listening(self):
        self.stop_animation()
        self.emoji_image.source = EMOJI_PATHS["listening"][0]
        self.emoji_image.reload()

    @mainthread
    def show_thinking(self):
        self.stop_animation()
        self.emoji_image.source = EMOJI_PATHS["thinking"][0]
        self.emoji_image.reload()

    @mainthread
    def show_emotion(self, emotion):
        self.stop_animation()
        self.current_emotion = emotion
        self.emotion_index = 0
        self.animate_emotion()

    def animate_emotion(self, dt=None):
        if self.current_emotion and self.current_emotion in EMOJI_PATHS:
            emojis = EMOJI_PATHS[self.current_emotion]
            self.emoji_image.source = emojis[self.emotion_index]
            self.emoji_image.reload()
            self.emotion_index = (self.emotion_index + 1) % len(emojis)
            self.animation_event = Clock.schedule_once(self.animate_emotion, 0.5)

    def stop_animation(self):
        if self.animation_event:
            self.animation_event.cancel()
            self.animation_event = None
        self.current_emotion = None
