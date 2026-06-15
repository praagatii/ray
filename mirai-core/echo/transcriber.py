import io
import os
import tempfile
from pathlib import Path


class EchoTranscriber:
    def __init__(self, engine_type: str = "google"):
        self.engine_type = engine_type
        self._whisper_model = None

    def transcribe(self, audio_data: bytes, sample_rate: int = 16000) -> str:
        if self.engine_type == "whisper":
            return self._transcribe_whisper(audio_data)
        return self._transcribe_google(audio_data, sample_rate)

    def transcribe_file(self, file_path: str) -> str:
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.AudioFile(file_path) as source:
                audio = r.record(source)
            return r.recognize_google(audio)
        except ImportError:
            return "Speech recognition not available (install SpeechRecognition)"
        except Exception as e:
            return f"Transcription error: {str(e)[:100]}"

    def listen_continuous(self, duration: int = 10, phrase_limit: int = 5) -> list[str]:
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            phrases = []
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                for _ in range(phrase_limit):
                    try:
                        audio = r.listen(source, timeout=duration, phrase_time_limit=5)
                        text = r.recognize_google(audio)
                        if text.strip():
                            phrases.append(text.strip())
                    except sr.WaitTimeoutError:
                        break
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError as e:
                        phrases.append(f"[STT error: {e}]")
                        break
            return phrases
        except ImportError:
            return ["Speech recognition not available (install SpeechRecognition)"]
        except Exception as e:
            return [f"Microphone error: {str(e)[:100]}"]

    def _transcribe_google(self, audio_data: bytes, sample_rate: int) -> str:
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            audio = sr.AudioData(audio_data, sample_rate, 2)
            return r.recognize_google(audio)
        except ImportError:
            return "Speech recognition not available"
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            return f"Transcription error: {str(e)[:100]}"

    def _transcribe_whisper(self, audio_data: bytes) -> str:
        try:
            import whisper
            if self._whisper_model is None:
                self._whisper_model = whisper.load_model("base")
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio_data)
                tmp_path = f.name
            result = self._whisper_model.transcribe(tmp_path)
            Path(tmp_path).unlink(missing_ok=True)
            return result.get("text", "").strip()
        except ImportError:
            return "Whisper not installed"
        except Exception as e:
            return f"Whisper error: {str(e)[:100]}"
