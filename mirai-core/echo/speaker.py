import os
import threading


class EchoSpeaker:
    def __init__(self, engine_type: str = "pyttsx"):
        self.engine_type = engine_type
        self._engine = None
        self._lock = threading.Lock()

    def speak(self, text: str, wait: bool = True) -> bool:
        if self.engine_type == "openai":
            return self._speak_openai(text, wait)
        return self._speak_pyttsx(text, wait)

    def speak_async(self, text: str):
        thread = threading.Thread(target=self.speak, args=(text, False), daemon=True)
        thread.start()

    def _speak_pyttsx(self, text: str, wait: bool) -> bool:
        try:
            import pyttsx3
            with self._lock:
                if self._engine is None:
                    self._engine = pyttsx3.init()
                    self._engine.setProperty("rate", 175)
                    self._engine.setProperty("volume", 0.9)
                self._engine.say(text)
                if wait:
                    self._engine.runAndWait()
            return True
        except Exception as e:
            print(f"[Echo TTS] pyttsx error: {e}")
            return False

    def _speak_openai(self, text: str, wait: bool) -> bool:
        try:
            from openai import OpenAI
            import tempfile
            import subprocess
            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                return self._speak_pyttsx(text, wait)
            client = OpenAI(
                api_key=api_key,
                base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            )
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(response.content)
                tmp_path = f.name
            subprocess.Popen(
                ["start", tmp_path], shell=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return True
        except Exception as e:
            print(f"[Echo TTS] OpenAI error: {e}")
            return self._speak_pyttsx(text, False)

    def stop(self):
        with self._lock:
            try:
                if self._engine:
                    self._engine.stop()
            except Exception:
                pass
