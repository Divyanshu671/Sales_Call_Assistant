import sounddevice as sd
import wave
import whisper
from pydub import AudioSegment
import numpy as np

whisper_model = whisper.load_model("base")

def record_audio(filename="output.wav", duration=4):
    RATE = 16000
    CHANNELS = 1

    print("Recording...")
    audio_data = sd.rec(int(duration * RATE), samplerate=RATE, channels=CHANNELS, dtype=np.int16)
    sd.wait()
    print("Recording finished.")

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(audio_data.tobytes())

def transcribe_audio(audio="output.wav"):
    segment = AudioSegment.from_wav(audio)
    segment = segment.set_channels(1).set_frame_rate(16000)
    segment.export(audio, format='wav')

    result = whisper_model.transcribe(audio, language="en")
    transcription = result["text"]
    return transcription