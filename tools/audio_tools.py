import os
from openai import AsyncOpenAI

class AudioTools:
    """Tools for audio processing using Groq Whisper and ElevenLabs TTS."""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"
        self.eleven_url = "https://api.elevenlabs.io/v1/text-to-speech"
        self.eleven_key = os.getenv("ELEVENLABS_API_KEY")
        self.default_voice = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL") # Bella/Victoria profile
        self.client = None

    async def transcribe(self, file_path: str) -> str:
        """Transcribes an audio file using Groq Whisper."""
        if not self.api_key:
            return "ERROR: GROQ_API_KEY no encontrada."
            
        if not self.client:
            self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
            
        try:
            with open(file_path, "rb") as file:
                transcription = await self.client.audio.transcriptions.create(
                    file=(os.path.basename(file_path), file.read()),
                    model="whisper-large-v3-turbo",
                    response_format="text"
                )
                return transcription
        except Exception as e:
            return f"ERROR en transcripción: {str(e)}"

    async def text_to_speech(self, text: str, voice_id: str = None) -> str:
        """Generates audio from text using ElevenLabs."""
        if not self.eleven_key:
            return "ERROR: ELEVENLABS_API_KEY no encontrada."
            
        import httpx
        voice = voice_id or self.default_voice
        url = f"{self.eleven_url}/{voice}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.eleven_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers)
                if response.status_code != 200:
                    return f"ERROR ElevenLabs: {response.text}"
                
                output_path = f"tmp_voice_{hash(text)}.mp3"
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return output_path
        except Exception as e:
            return f"ERROR en TTS: {str(e)}"

    async def list_voices(self) -> list:
        """Fetch available voices from ElevenLabs."""
        if not self.eleven_key:
            return [{"error": "ELEVENLABS_API_KEY no encontrada."}]
            
        import httpx
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {"xi-api-key": self.eleven_key}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                if response.status_code != 200:
                    return [{"error": f"Error: {response.text}"}]
                
                data = response.json()
                return [{"name": v["name"], "id": v["voice_id"]} for v in data.get("voices", [])]
        except Exception as e:
            return [{"error": str(e)}]
