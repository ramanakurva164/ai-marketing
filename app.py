import streamlit as st
import requests
from gtts import gTTS
import google.generativeai as genai

# ---------------- Configuration ----------------
# Load secrets from Streamlit
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
HF_API_TOKEN = st.secrets["HF_API_TOKEN"]

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Hugging Face Image Gen API
HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HF_HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}


# ---------------- Functions ----------------
def generate_text(product, audience):
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
    tts = gTTS(text=script, lang="en")
    tts.save(filename)
    return filename


# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="AI Marketing Campaign Generator", layout="wide")
st.markdown(
    """
    <style>
        .main-title {
            text-align: center;
            font-size: 36px !important;
            color: #4CAF50;
        }
        .section {
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 25px;
            background-color: #1e1e1e;
            color: #f5f5f5;
        }
        .stTextInput > div > div > input {
            border-radius: 8px;
            padding: 10px;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            font-size: 18px;
            padding: 12px 24px;
            border-radius: 10px;
            transition: all 0.3s ease-in-out;
        }
        .stButton button:hover {
            background-color: #388E3C;
            transform: scale(1.05);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="main-title">🚀 AI Marketing Campaign Generator</h1>', unsafe_allow_html=True)

# Input Section
with st.form("campaign_form"):
    st.markdown("### 🛍️ Enter Product Details")
    product = st.text_input("", "EcoSip Smart Bottle - Eco-friendly hydration tracking bottle")

    st.markdown("### 🎯 Enter Target Audience")
    audience = st.text_input("", "18–35 year old health-conscious professionals in urban cities")

    submitted = st.form_submit_button("✨ Generate Campaign ✨")

if submitted:
    with st.spinner("⚡ Crafting your campaign..."):
        # Layout with two columns
        left_col, right_col = st.columns([2, 1])

        # Step 1: Text Campaign (Left)
        with left_col:
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.subheader("📢 Generated Campaign Content")
            campaign_text = generate_text(product, audience)
            st.write(campaign_text)
            st.markdown('</div>', unsafe_allow_html=True)

        # Step 2 & 3: Image + Audio (Right)
        with right_col:
            # Image
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.subheader("🎨 Ad Creative")
            img_path = generate_image(f"Ad creative for {product} targeting {audience}")
            if img_path:
                st.image(img_path, caption="Generated Ad Creative")
            st.markdown('</div>', unsafe_allow_html=True)

            # Audio
            st.markdown('<div class="section">', unsafe_allow_html=True)
            st.subheader("🎧 Audio Ad")
            audio_path = generate_audio(campaign_text.split("\n")[0])
            st.audio(audio_path)
            st.markdown('</div>', unsafe_allow_html=True)
