import streamlit as st
import os
import requests
from gtts import gTTS
import tempfile
import google.generativeai as genai

# ========================
# CONFIG
# ========================
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"] 
HF_API_TOKEN = st.secrets["HF_API_KEY"]

# ========================
# HELPER FUNCTIONS
# ========================
def generate_campaign(product, audience):
    """Generate campaign text with Gemini."""
    prompt = f"""
    Generate a creative marketing campaign for:
    Product: {product}
    Target Audience: {audience}

    Include the following sections:
    1. Ad Copy
    2. Email Marketing Copy
    3. Social Media Posts
    4. Radio Script
    5. Audio Brief (short script suitable for voice ad)
    """
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text


def generate_image(prompt):
    """Generate an image using Hugging Face Inference API (Stable Diffusion)."""
    API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}

    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp_file.write(response.content)
        tmp_file.close()
        return tmp_file.name
    else:
        st.error(f"Image generation failed: {response.text}")
        return None


def generate_audio(text):
    """Generate audio using gTTS."""
    if not text.strip():
        raise ValueError("No text provided for audio generation.")

    tts = gTTS(text=text, lang="en")
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp_file.name)
    return tmp_file.name


def extract_section(campaign_text: str, section_name: str) -> str:
    """Extract specific section content from campaign text."""
    lines = campaign_text.splitlines()
    capture = False
    section = []
    for line in lines:
        if line.strip().lower().startswith(section_name.lower()):
            capture = True
            continue
        if capture:
            if line.strip() == "" or line.strip().endswith(":"):
                break
            section.append(line.strip())
    return "\n".join(section).strip()


# ========================
# STREAMLIT UI
# ========================
st.set_page_config(page_title="AI Marketing Campaign Generator", layout="wide")

st.markdown(
    """
    <style>
    body {background-color: #f9f9f9;}
    .title {text-align: center; font-size: 40px; color: #4CAF50; font-weight: bold;}
    .section {padding: 20px; border-radius: 12px; margin-bottom: 20px;}
    .ad {background-color: #E8F5E9;}
    .email {background-color: #E3F2FD;}
    .social {background-color: #F3E5F5;}
    .radio {background-color: #FFF3E0;}
    .audio {background-color: #ECEFF1;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1 class='title'>🤖 AI Marketing Campaign Generator</h1>", unsafe_allow_html=True)

with st.form("campaign_form"):
    product = st.text_input("Enter your product details:", "Eco-friendly Water Bottle")
    audience = st.text_input("Enter target audience:", "Young professionals, fitness enthusiasts")
    submitted = st.form_submit_button("Generate Campaign")

if submitted:
    with st.spinner("✨ Generating campaign..."):
        campaign_text = generate_campaign(product, audience)

    st.subheader("📊 Campaign Results")

    # Sections with icons + colors
    sections = {
        "Ad Copy": ("📝", "ad"),
        "Email Marketing Copy": ("📧", "email"),
        "Social Media Posts": ("📱", "social"),
        "Radio Script": ("🎙️", "radio"),
        "Audio Brief": ("🎧", "audio"),
    }

    for section, (icon, css_class) in sections.items():
        st.markdown(f"<div class='section {css_class}'>", unsafe_allow_html=True)
        st.subheader(f"{icon} {section}")

        content = extract_section(campaign_text, section)
        if content:
            st.markdown(f"<p style='font-size:16px; line-height:1.6;'>{content}</p>", unsafe_allow_html=True)
        else:
            st.info(f"No {section} found in the campaign text.")

        # Special case: Audio
        if section == "Audio Brief" and content:
            try:
                audio_path = generate_audio(content)
                st.audio(audio_path)
            except Exception as e:
                st.error(f"Audio generation failed: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    # Generate Image
    st.subheader("🖼️ Generated Ad Image")
    img_prompt = f"{product} for {audience}, professional ad style"
    img_path = generate_image(img_prompt)
    if img_path:
        st.image(img_path, caption="Generated Campaign Image", use_container_width=True)
