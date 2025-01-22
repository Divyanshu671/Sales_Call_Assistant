import pyaudio
import wave
import whisper
from pydub import AudioSegment

whisper_model = whisper.load_model("base")

def record_audio(filename="output.wav", duration=4):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = duration
    WAVE_OUTPUT_FILENAME = filename

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_audio(audio="output.wav"):
    segment = AudioSegment.from_wav(audio)
    segment = segment.set_channels(1).set_frame_rate(16000)
    segment.export(audio, format='wav')

    result = whisper_model.transcribe(audio, language="en")
    transcription = result["text"]
    return transcription