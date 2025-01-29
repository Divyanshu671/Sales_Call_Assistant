from pydub import AudioSegment
import numpy as np
from nltk.sentiment import  SentimentIntensityAnalyzer
from nltk import download

download('vader_lexicon')

sia = SentimentIntensityAnalyzer()

def analyze_text(text):
    sentiment_scores = sia.polarity_scores(text)
    if sentiment_scores["compound"] > 0.05:
        sentiment = "Positive"  
    elif sentiment_scores["compound"] < -0.05:
        sentiment = "Negative"  
    else:
        sentiment = "Neutral"
    return [sentiment, sentiment_scores]
    
def analyze_tone(audio):
    au = AudioSegment.from_file(audio)

    rms = au.rms
    amplitude = np.mean(np.abs(au.get_array_of_samples()))
    tone_analysis={
        "duration_ms": len(au),
        "avg_amplitude": amplitude,
        "rms": rms,
    }

    if rms>1000:
        tone="Energetic"
    elif rms>500:
        tone="Moderate"
    else:
        tone="Calm"
    tone_analysis["tone"] = tone
    return tone_analysis

def sentiment_analysis(audio,text):
    result_tone = analyze_tone(audio)
    result_text = analyze_text(text)

    return {
        "Tone" : result_tone,
        "Text" : result_text
    }