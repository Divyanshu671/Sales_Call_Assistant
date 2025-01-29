import faiss
import pandas as pd
import spacy
import numpy as np
from groq import Groq
import os
from dotenv import load_dotenv

# load_dotenv()
# key = os.getenv("GROQ_API_KEY")
key = os.secrets["GROQ_API_KEY"]
client = Groq(api_key=key)
nlp = spacy.load("en_core_web_md")
dataset = pd.read_excel("data/Conversation_data.xlsx")


def load_data():
    laptops = pd.read_csv("data/laptop_price.csv",encoding='latin1')
    mobiles = pd.read_csv("data/Flipkart_Mobiles.csv",encoding='latin1')

    return [laptops,mobiles]

def build_faiss_index(data):
    embeddings = [nlp(text).vector for text in data]

    dimension = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    return index

def recommend_product(query, data, index):
    k=10
    query_vector = nlp(query).vector.reshape(1,-1)

    distances, indices = index.search(query_vector, k)

    recommendations = data.iloc[indices[0]]

    if "Brand" in recommendations.columns:  
        recommendations = recommendations.groupby("Brand").head(2) 
        recommendations = recommendations.head(5)
    elif "Company" in recommendations.columns:  
        recommendations = recommendations.groupby("Company").head(2) 
        recommendations = recommendations.head(5)
    else:
        recommendations = recommendations.head(5)

    system_prompt = {
        "role": "system",
        "content": f"I have found {len(recommendations)} recommendations based on the user's query: '{query}'. "
                   f"Please generate a professional and customer-friendly response with the following product details:\n"
                   f"{recommendations}"
    }

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",  
            messages=[system_prompt],
            max_tokens=200,
            temperature=1.2
        )

        assistant_response = response.choices[0].message.content
        return [recommendations,assistant_response]

    except Exception as e:
        return f"Recommendation Error: {e}"

def generate_objection_response(transcription, text_sentiment, tone_sentiment):
    system_prompt = {
        "role": "system",
        "content": "You are a assistant. Respond in brief with an objection handling strategy "
        "while giving suggestion based on the user's input text, text sentiment, and tone sentiment and relevant "
        "insights from the dataset if provided and no need to give premise."
    }

    chat_history = [system_prompt]

    user_message = f"""
    Text: {transcription}
    Text Sentiment: {text_sentiment}
    Tone Sentiment: {tone_sentiment}
    """

    try:
        dataset_summary = summarize_dataset(dataset)
        user_message += f"\nDataset Insights: {dataset_summary}"
    except FileNotFoundError:
        user_message += "\nDataset Insights: Conversation history dataset not found."
    except Exception as e:
        user_message += f"\nDataset Insights: Error loading dataset - {e}"

    chat_history.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",  
            messages=chat_history,
            max_tokens=100,
            temperature=1.2
        )

        assistant_response = response.choices[0].message.content
        return assistant_response

    except Exception as e:
        return f"Response Error: {e}"
    
def summarize_dataset(dataset):
    if dataset.empty:
        return "No conversation history available."
    
    recent_history = dataset.tail(3)
    summary = "Recent Conversation:\n" + recent_history.to_string(index=False)
    return summary

def detect_product_type(text):
    product_keywords = {
        "laptops": ["laptop", "notebook", "MacBook", "Ultrabook", "gaming laptop","laptops"],
        "mobiles": ["mobile", "smartphone", "phone", "iPhone", "Android", "mobiles"]
    }

    for product_type, keywords in product_keywords.items():
        if any(keyword.lower() in text.lower() for keyword in keywords):
            return product_type
    
    return "unknown"

def workflow(query):
    product_type = detect_product_type(query[0])
    if product_type=="unknown":
        return ["none","Not available",generate_objection_response(query[0],query[1],query[2])]
    laptops, mobiles = load_data()
    data = laptops if product_type.lower()=="laptops" else mobiles

    index = build_faiss_index(data)

    recommendations,recommendation_response = recommend_product(query[0], data, index)

    objection_response = generate_objection_response(query[0], query[1], query[2])

    return [recommendations, recommendation_response, objection_response]

def summary():
    message = dataset.to_string(index=False)
    system_prompt = {
        "role": "system",
        "content": "You are a helpful assistant. Respond in brief where you are summarizing all the previous conversations"
        "based on message , text sentiment, tone sentiment and give a combined summary upto 100 words"
        "in a compact text format and there is no need to give premise."
    }

    chat_history = [system_prompt]


    try:
        dataset_summary = message
        user_message = f"\nDataset Insights: {dataset_summary}"
    except FileNotFoundError:
        user_message = "\nDataset Insights: Conversation history dataset not found."
    except Exception as e:
        user_message = f"\nDataset Insights: Error loading dataset - {e}"

    chat_history.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",  
            messages=chat_history,
            max_tokens=200,
            temperature=1.2
        )

        assistant_response = response.choices[0].message.content
        return assistant_response

    except Exception as e:
        return f"Response Error: {e}"