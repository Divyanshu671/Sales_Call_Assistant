import sounddevice as sd
import wave
import os
from groq import Groq
groq_api_key = os.getenv("GROQ_API_KEY")  
client = Groq(api_key=groq_api_key)

def record_audio(filename="data/output.wav", duration=4):
    CHANNELS = 2
    RATE = 16000  

    try:
        recording = sd.rec(int(duration * RATE), samplerate=RATE, channels=CHANNELS, dtype='int16')
        sd.wait()

        with wave.open(filename, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(RATE)
            wf.writeframes(recording.tobytes())

    except Exception as e:
        raise RuntimeError(f"Error recording audio: {e}")




def transcribe_audio(audio_path="data/output.wav"):
    try:
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                file=("audio.wav", audio_file.read()),  
                model="whisper-large-v3-turbo",         
                response_format="json",                 
                language="en",                          
                temperature=0.0                         
            )
        
        return response.text

    except FileNotFoundError:
        print(f"❌ File not found: {audio_path}")
    except Exception as e:
        print(f"⚠️ Error transcribing audio: {e}")
