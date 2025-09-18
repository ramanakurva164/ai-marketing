import os
import requests
import streamlit as st
from dotenv import load_dotenv
from gtts import gTTS
import google.generativeai as genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
HF_API_TOKEN = st.secrets["HF_API_TOKEN"]

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Hugging Face Image Gen API
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HF_HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}


def generate_text(product, audience):
    """Generate campaign text using Gemini"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    Create a full marketing campaign for:
    Product: {product}
    Target Audience: {audience}

    Output:
    - Ad Copy (headline + tagline)
    - Email Campaign (subject + body)
    - Social Media Post
    - Radio/Podcast Ad Script (30 sec)
    """
    response = model.generate_content(prompt)
    return response.text


def generate_image(prompt, filename="ad_creative.png"):
    """Generate ad creative using Hugging Face Stable Diffusion"""
    payload = {"inputs": prompt}
    response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload)

    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        return filename
    else:
        st.error(f"Image generation failed: {response.text}")
        return None


def generate_audio(script, filename="ad_audio.mp3"):
    """Generate free TTS audio ad using gTTS"""
    tts = gTTS(text=script, lang="en")
    tts.save(filename)
    return filename


# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="AI Marketing Campaign Generator", layout="wide")
st.title("🚀 AI Marketing Campaign Generator")

with st.form("campaign_form"):
    product = st.text_input("🛍️ Enter Product Details", "EcoSip Smart Bottle - Eco-friendly hydration tracking bottle")
    audience = st.text_input("🎯 Enter Target Audience", "18–35 year old health-conscious professionals in urban cities")
    submitted = st.form_submit_button("Generate Campaign")

if submitted:
    with st.spinner("Generating campaign..."):
        # Step 1: Text
        campaign_text = generate_text(product, audience)
        st.subheader("📢 Generated Campaign Content")
        st.write(campaign_text)

        # Step 2: Image
        st.subheader("🎨 Ad Creative")
        img_path = generate_image(f"Ad creative for {product} targeting {audience}")
        if img_path:
            st.image(img_path, caption="Generated Ad Creative")

        # Step 3: Audio
        st.subheader("🎧 Audio Ad")
        audio_path = generate_audio(campaign_text.split("\n")[0])  # take ad copy for TTS
        st.audio(audio_path)
