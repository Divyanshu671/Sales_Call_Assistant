import pyaudio
import wave
import whisper
from pydub import AudioSegment

whisper_model = whisper.load_model("base")

def record_audio(filename="output.wav", duration=4):
    p = pyaudio.PyAudio()  
    INPUT_DEVICE_INDEX = 0

    input_device = p.get_device_info_by_index(INPUT_DEVICE_INDEX)
    CHANNELS = input_device['maxInputChannels']
    RATE = int(input_device['defaultSampleRate']) 
    CHUNK = 1024  
    FORMAT = pyaudio.paInt16  
    try:
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=INPUT_DEVICE_INDEX,
                        frames_per_buffer=CHUNK)

        frames = []  
        for _ in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(filename, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

    except Exception as e:
        print(f"Error recording audio: {e}")
        p.terminate()

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
