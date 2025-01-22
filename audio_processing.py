import sounddevice as sd
import streamlit as st
import wave
import whisper
from pydub import AudioSegment
import numpy as np

whisper_model = whisper.load_model("base")

# def check_audio_device():
#     devices = sd.query_devices()
#     for i, device in enumerate(devices):
#         st.write(f"Device {i}: {device['name']}")

def record_audio(filename="output.wav", duration=4, device_id=None):
    RATE = 16000
    CHANNELS = 1

    # check_audio_device()

    try:
        if device_id is None:
            device_id = 0
        
        print("Recording...")
        audio_data = sd.rec(int(duration * RATE), samplerate=RATE, channels=CHANNELS, dtype=np.int16, device=device_id)
        sd.wait()
        print("Recording finished.")

        with wave.open(filename, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(RATE)
            wf.writeframes(audio_data.tobytes())

    except sd.PortAudioError as e:
        print(f"Error recording audio: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def transcribe_audio(audio="output.wav"):
    try:
        segment = AudioSegment.from_wav(audio)
        segment = segment.set_channels(1).set_frame_rate(16000)
        segment.export(audio, format='wav')

        result = whisper_model.transcribe(audio, language="en")
        transcription = result["text"]
        return transcription

    except Exception as e:
        print(f"Error transcribing audio: {e}")