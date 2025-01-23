import streamlit as st
from audio_processing import record_audio, transcribe_audio
from sentiment_analyzing import sentiment_analysis
from storing_conversations import store_response
from crmd_system import workflow
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from openpyxl import load_workbook
from pathlib import Path
import base64
import time
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Styling
st.markdown(
    """
    <style>
    /* App Background */
    .main {
        background: linear-gradient(135deg, #1f3c88, #1b1f3b); /* Glamorous gradient */
        color: white; /* White text for contrast */
        font-family: 'Segoe UI', sans-serif; /* Modern font */
        padding: 20px;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #1b1f3b, #2c3e50); /* Gradient sidebar */
        color: white;
        box-shadow: 2px 0 10px rgba(0, 0, 0, 0.5); /* Subtle shadow */
    }

    /* Sidebar titles and menu text */
    .css-1d391kg p, .css-1v3fvcr h1, .css-1v3fvcr h2 {
        color: white; /* White text in sidebar */
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(90deg, #6a11cb, #2575fc); /* Gradient button */
        color: white;
        font-size: 16px;
        font-weight: bold;
        border: none;
        border-radius: 20px; /* Fully rounded buttons */
        padding: 10px 20px;
        transition: 0.3s ease-in-out;
    }
    .stButton button:hover {
        transform: scale(1.05); /* Slight zoom effect */
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.3); /* Glow on hover */
    }

    /* Curved box for displaying results */
    .curved-box {
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.1); /* Transparent background */
        backdrop-filter: blur(10px); /* Blur effect for a glassy look */
        padding: 20px;
        margin: 20px 0;
        color: white;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5); /* Subtle shadow */
    }

    /* Titles and subtitles */
    .title {
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #6a11cb, #2575fc); /* Gradient title */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        font-size: 15px;
        font-weight: 250;
        text-align: center;
        color: #d1d9e6; /* Light gray text for subtitles */
    }

    /* Output text styling */
    .output-text {
        color: red; /* Vibrant teal for outputs */
        font-size: 18px;
        font-weight: bold;
    }

    /* Scrollable areas */
    .scrollable-box {
        max-height: 400px;
        overflow-y: auto;
        background: rgba(255, 255, 255, 0.05); /* Slightly transparent background */
        padding: 50px;
        border-radius: 10px;
        box-shadow: inset 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    /* Positioning logos at the top-right corner */
        .logo-container {
            position: absolute;
            top: 10px;
            right: 20px;
            display: flex;
            gap: 10px;
        }
        .logo-container img {
            width: 50px;
            height: auto;
            border-radius: 10px; /* Optional rounded corners */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Optional shadow */
            transition: transform 0.3s ease-in-out;
        }
        .logo-container img:hover {
            transform: scale(1.1); /* Slight zoom effect on hover */
        }
        .complete {
            background-color: white;
            color: black;
            font-size: 18px;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# LOGO
def encode_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
MOBILE_LOGO_PATH = "data/mobile.jpg"
LAPTOP_LOGO_PATH = "data/laptop.jpg"
if Path(MOBILE_LOGO_PATH).is_file() or not Path(LAPTOP_LOGO_PATH).is_file():
    # Encode images
    mobile_logo_base64 = encode_image_base64(MOBILE_LOGO_PATH)
    laptop_logo_base64 = encode_image_base64(LAPTOP_LOGO_PATH)
    st.markdown(
        f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{mobile_logo_base64}" alt="Mobile Logo">
            <img src="data:image/png;base64,{laptop_logo_base64}" alt="Laptop Logo">
        </div>
        """,
        unsafe_allow_html=True,
    )

# Sidebar
st.sidebar.title("Features")
menu = st.sidebar.radio("Go to", ["Home", "Dashboard"])

st.markdown("<h1 class='title'>AI Sales Call Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your AI-powered assistant for smarter sales</p>", unsafe_allow_html=True)

# Processing
if "recording_flag" not in st.session_state:
    st.session_state.recording_flag = False
if "products" not in st.session_state:
    st.session_state.products = {}
if "final_sentiment" not in st.session_state:
    st.session_state.final_sentiment = {}
if "index" not in st.session_state:
    st.session_state.index = 0


history_file = Path("Conversation_data.xlsx")
st.session_state.conversation_history_df = pd.read_excel(history_file, engine='openpyxl')

def process_audio_and_analyze():
    while True:
        time.sleep(5)
        st.session_state.index += 1
        if not st.session_state.recording_flag:
            break
        try:
            record_audio()
            with st.spinner("Processing audio..."):
                transcription = transcribe_audio()
                transcription = transcription if len(transcription) else "NaN"
                st.session_state.final_sentiment = sentiment_result = sentiment_analysis("output.wav", transcription)
                query = [transcription, sentiment_result["Text"], sentiment_result["Tone"]]
                response = workflow(query)
                st.session_state.products = response[0]
                store_response(
                  [st.session_state.index], [query[0]], [query[1][0]], [query[2]["tone"]], [response[1]], [response[2]]
                )
        except Exception as e:
            st.write(e)
            break

def plot_sentiment_data():
    if "conversation_history_df" in st.session_state and not st.session_state.conversation_history_df.empty:
        data = st.session_state.conversation_history_df

        sentiment_map = {"Positive": 1, "Neutral": 0, "Negative": -1, "Energetic": 1, "Moderate": 0, "Calm": -1}
        data["Tone Sentiment (Numeric)"] = data["Tone Sentiment"].map(sentiment_map)
        data["Text Sentiment (Numeric)"] = data["Text Sentiment"].map(sentiment_map)

        if data[["Tone Sentiment (Numeric)", "Text Sentiment (Numeric)"]].isnull().all().all():
            st.info("No valid sentiment data available for plotting.")
            return

        fig, ax = plt.subplots(figsize=(10, 6))
        index = np.arange(len(data))
        bar_width = 0.35

        text_bars = ax.bar(index, data["Text Sentiment (Numeric)"], bar_width, label="Text Sentiment", color="blue")
        tone_bars = ax.bar(index + bar_width, data["Tone Sentiment (Numeric)"], bar_width, label="Tone Sentiment", color="orange")

        ax.set_xlabel("Index")
        ax.set_ylabel("Sentiment Value")
        ax.set_title("Sentiment Analysis - Bar Chart")
        ax.set_xticks(index + bar_width / 2)
        ax.set_xticklabels(data["Index"].astype(str), rotation=45)
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("No conversation history available to plot.")

if menu == "Home":
    st.markdown("#### Ask about products by telling me")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Say it >"):
            st.info("Recording... ")
            st.session_state.recording_flag = True
            process_audio_and_analyze()
    with col2:
        if st.button("Stop"):
            st.session_state.recording_flag = False
            st.info("Recording Stopped!")
    if len(st.session_state.conversation_history_df):
        combined_content = f"""<div class='curved-box scrollable-box'>"""
        st.markdown("<h3 class='subtitle'>AI Assistant:</h3>", unsafe_allow_html= True)
        for i, row in st.session_state.conversation_history_df.iterrows():
            content = f"""<div>
                Query:{row["Message"]}
                \nText Sentiment:{row['Text Sentiment']}
                \nTone Sentiment:{row['Tone Sentiment']}
                \nRecommendation:{row['recommendation']}
                Response:{row['response']}
            </div>"""
            combined_content+=content
        combined_content += """</div>"""
        st.markdown(combined_content,unsafe_allow_html=True)

elif menu == "Dashboard":
    st.markdown("<h3 class='subtitle'>Summary:</h3>", unsafe_allow_html= True)
    if not len(st.session_state.conversation_history_df):
        st.info("No Coversation History Found.")
    else:
        if st.button("Delete Conversations"):
            try:
                history_file = Path("Conversation_data.xlsx")
                if history_file.is_file():
                    workbook = load_workbook(history_file)
                    sheet = workbook.active
                    
                    sheet.delete_rows(2, sheet.max_row + 1)  
                    workbook.save(history_file)  
                    workbook.close()
                    
                    st.success("All conversations deleted successfully!")
                    st.session_state.conversation_history_df = pd.DataFrame(columns=["Message", "Text Sentiment", "Tone Sentiment", "recommendation", "response"])
                else:
                    st.info("No file found to delete.")
            except Exception as e:
                st.error(f"Error while deleting conversations: {e}")
        
        with st.expander("View Full summary", expanded=True):
            plot_sentiment_data()
            for i, row in st.session_state.conversation_history_df.iterrows():
                st.markdown(f"""<div class='curved-box scrollable-box'>
                    <div class='output-text'>Query:{row['Message']}</div>
                    \nText Sentiment:{row['Text Sentiment']}
                    \nTone Sentiment:{row['Tone Sentiment']}
                    \nRecommendation:{row['recommendation']}
                    Response:{row['response']}
                </div>""", unsafe_allow_html=True)