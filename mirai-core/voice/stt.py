import io
import os
import tempfile
from pathlib import Path


class SpeechToText:
    def __init__(self, engine: str = "google"):
        self.engine = engine

    def transcribe_file(self, audio_path: str) -> str:
        if self.engine == "google":
            return self._transcribe_google(audio_path)
        elif self.engine == "whisper":
            return self._transcribe_whisper(audio_path)
        return ""

    def transcribe_bytes(self, audio_bytes: bytes) -> str:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name
        try:
            return self.transcribe_file(tmp_path)
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass

    def _transcribe_google(self, audio_path: str) -> str:
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)
            return recognizer.recognize_google(audio)
        except ImportError:
            return "SpeechRecognition library not installed"
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            return f"STT error: {e}"

    def _transcribe_whisper(self, audio_path: str) -> str:
        try:
            import openai
            client = openai.OpenAI()
            with open(audio_path, "rb") as f:
                transcript = client.audio.transcriptions.create(model="whisper-1", file=f)
            return transcript.text
        except Exception as e:
            return f"Whisper error: {e}"

    def listen_from_mic(self, duration: int = 5) -> str:
        try:
            import sounddevice as sd
            import soundfile as sf
            import speech_recognition as sr

            fs = 16000
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
            sd.wait()

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                sf.write(f.name, recording, fs)
                tmp_path = f.name

            recognizer = sr.Recognizer()
            with sr.AudioFile(tmp_path) as source:
                audio = recognizer.record(source)
            result = recognizer.recognize_google(audio)
            os.unlink(tmp_path)
            return result
        except ImportError:
            return "Microphone libraries not installed"
        except Exception as e:
            return f"Mic error: {e}"
