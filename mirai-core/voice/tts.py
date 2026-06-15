import os
import tempfile


class TextToSpeech:
    def __init__(self, engine: str = "pyttsx3"):
        self.engine = engine

    def speak(self, text: str) -> str:
        if self.engine == "pyttsx3":
            return self._speak_pyttsx3(text)
        elif self.engine == "openai":
            return self._speak_openai(text)
        return ""

    def _speak_pyttsx3(self, text: str) -> str:
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            return text
        except ImportError:
            return "pyttsx3 not installed"
        except Exception as e:
            return f"TTS error: {e}"

    def _speak_openai(self, text: str) -> str:
        try:
            from openai import OpenAI
            client = OpenAI()
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                response = client.audio.speech.create(model="tts-1", voice="alloy", input=text)
                response.stream_to_file(f.name)
                tmp_path = f.name
            return tmp_path
        except Exception as e:
            return f"OpenAI TTS error: {e}"

    def speak_async(self, text: str):
        import threading
        thread = threading.Thread(target=self.speak, args=(text,))
        thread.daemon = True
        thread.start()
