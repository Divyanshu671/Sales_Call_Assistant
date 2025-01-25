import sounddevice as sd
import wave
import whisper
from pydub import AudioSegment

whisper_model = whisper.load_model("turbo")

def record_audio(filename="output.wav", duration=4):
    INPUT_DEVICE_INDEX = 0
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024  
    devices = sd.query_devices()
    print(devices)
    try:
        recording = sd.rec(int(duration * RATE), samplerate=RATE, channels=CHANNELS, dtype='int16', device=INPUT_DEVICE_INDEX)
        sd.wait()

        with wave.open(filename, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(RATE)
            wf.writeframes(recording.tobytes())

    except Exception as e:
        print(f"Error recording audio: {e}")

def transcribe_audio(audio="output.wav"):
    try:
        import os
        if not os.path.exists(audio):
            raise FileNotFoundError(f"Audio file {audio} does not exist!")

        segment = AudioSegment.from_wav(audio)
        segment = segment.set_channels(1).set_frame_rate(16000)
        segment.export(audio, format='wav')

        result = whisper_model.transcribe(audio, language="en")
        transcription = result["text"]
        return transcription

    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"Error transcribing audio: {e}")
