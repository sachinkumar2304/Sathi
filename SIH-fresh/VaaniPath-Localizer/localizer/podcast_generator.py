# =============================================================================
# THIS ENTIRE FILE IS DISABLED — Not used in the PM-AJAY prototype.
# Original code preserved below as a multi-line comment for future reference.
# =============================================================================

"""
import logging
import json
import base64
import os
import shutil
import random
import asyncio
from pathlib import Path
from typing import List, Dict, Optional

try:
    import httpx
except ImportError:
    httpx = None
    logging.warning("httpx not installed — HTTP features unavailable")

try:
    from pydub import AudioSegment
except ImportError:
    AudioSegment = None
    logging.warning("pydub not installed — audio merging will use fallback")

try:
    from elevenlabs.client import ElevenLabs
except ImportError:
    ElevenLabs = None
    logging.warning("elevenlabs not installed — will use gTTS fallback")

try:
    import groq
except ImportError:
    groq = None
    logging.warning("groq not installed — will use mock scripts")

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except (ImportError, Exception) as e:
    logging.warning(f"static_ffmpeg unavailable: {e} — relying on system ffmpeg or fallback")

# Constants
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

class PodcastGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Groq Client
        self.groq_client = None
        if groq and GROQ_API_KEY:
            try:
                self.groq_client = groq.Groq(api_key=GROQ_API_KEY)
            except Exception as e:
                print(f"Failed to initialize Groq: {e}")

        # Initialize ElevenLabs Client
        self.elevenlabs_client = None
        if ElevenLabs and ELEVENLABS_API_KEY:
            try:
                self.elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
            except Exception as e:
                print(f"Failed to initialize ElevenLabs: {e}")

        # Voice Configuration
        self.voices = {
            "Alex": {
                "gender": "male",
                "elevenlabs_id": "pNInz6obpgDQGcFmaJgB",
                "edge_voice": "en-US-GuyNeural"
            },
            "Jordan": {
                "gender": "female",
                "elevenlabs_id": "21m00Tcm4TlvDq8ikWAM",
                "edge_voice": "en-US-JennyNeural"
            }
        }

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        import PyPDF2
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\\n"
            return text.strip()
        except Exception as e:
            print(f"Failed to extract text from PDF: {e}")
            return ""

    async def generate_script(self, text: str, language: str) -> List[Dict[str, str]]:
        if not self.groq_client:
            return self._get_mock_script(language)

        prompt = f"Create a podcast script between two hosts, Alex and Jordan, based on: {text[:4000]}"

        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a professional podcast script writer."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            content = chat_completion.choices[0].message.content
            script = json.loads(content)
            if isinstance(script, dict):
                if "dialogue" in script:
                    return script["dialogue"]
                for key, value in script.items():
                    if isinstance(value, list):
                        return value
            if isinstance(script, list):
                return script
            return self._get_mock_script(language)
        except Exception as e:
            return self._get_mock_script(language)

    def _get_mock_script(self, language: str) -> List[Dict[str, str]]:
        if language.lower() == "hindi":
            return [
                {"speaker": "Alex", "text": "Namaste doston!"},
                {"speaker": "Jordan", "text": "Bilkul Alex!"},
            ]
        else:
            return [
                {"speaker": "Alex", "text": "Hello everyone!"},
                {"speaker": "Jordan", "text": "Absolutely Alex!"},
            ]

    async def generate_audio(self, script: List[Dict[str, str]]) -> str:
        audio_segments = []
        for i, line in enumerate(script):
            speaker = line["speaker"]
            text = line["text"]
            filename = f"segment_{i}_{speaker}.mp3"
            filepath = self.output_dir / filename
            if self.elevenlabs_client:
                try:
                    voice_id = self.voices.get(speaker, {}).get("elevenlabs_id")
                    if voice_id:
                        audio = self.elevenlabs_client.text_to_speech.convert(
                            text=text, voice_id=voice_id, model_id="eleven_multilingual_v2"
                        )
                        with open(filepath, "wb") as f:
                            for chunk in audio:
                                f.write(chunk)
                        audio_segments.append(filepath)
                        continue
                except Exception as e:
                    pass
            try:
                from gtts import gTTS
                tts = gTTS(text=text, lang='en', tld='co.in')
                tts.save(str(filepath))
                audio_segments.append(filepath)
            except Exception as e:
                pass

        if not audio_segments:
            raise Exception("Failed to generate any audio segments")

        output_filename = f"podcast_final_{random.randint(1000, 9999)}.mp3"
        output_path = self.output_dir / output_filename

        if AudioSegment is not None:
            try:
                combined = AudioSegment.empty()
                silence = AudioSegment.silent(duration=500)
                for seg_path in audio_segments:
                    segment = AudioSegment.from_mp3(str(seg_path))
                    combined += segment + silence
                combined.export(str(output_path), format="mp3")
            except Exception:
                with open(output_path, 'wb') as outfile:
                    for seg_path in audio_segments:
                        with open(seg_path, 'rb') as infile:
                            outfile.write(infile.read())
        else:
            with open(output_path, 'wb') as outfile:
                for seg_path in audio_segments:
                    with open(seg_path, 'rb') as infile:
                        outfile.write(infile.read())

        for seg_path in audio_segments:
            try:
                os.remove(seg_path)
            except OSError:
                pass

        return str(output_path)

    async def create_podcast(self, text: str, language: str) -> str:
        script = await self.generate_script(text, language)
        audio_path = await self.generate_audio(script)
        return audio_path
"""
