import os
import streamlit as st
import google.generativeai as genai
import requests
from dotenv import load_dotenv
from diffusers.pipelines.pipeline_utils import DiffusionPipeline
from db import save_campaign
from elevenlabs.client import ElevenLabs
from elevenlabs import play

# Load environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", st.secrets.get("GEMINI_API_KEY"))
if not api_key:
    st.error("❌ No API key found. Please set GEMINI_API_KEY in Streamlit secrets or as an environment variable.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash-lite")

# Streamlit UI
st.set_page_config(page_title="AI Marketing Campaign Generator", layout="wide")
st.title("🤖 AI Marketing Campaign Generator")

with st.form("campaign_form"):
    product = st.text_input("Enter your product details")
    audience = st.text_input("Target Audience")
    submitted = st.form_submit_button("Generate Campaign")

if submitted:
    st.info("Generating with Gemini…")
    prompt = f"""
    Generate a marketing campaign for product: {product}
    Target audience: {audience}
    Include:
    1. Ad copy
    2. Email campaign
    3. Social media posts
    """

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    response = model.generate_content(prompt)
    response = model.generate_content(prompt)
    text_output = response.text
    # image API (replace with Stable Diffusion/DALL·E)
    st.info("Generating image with Deep-Image.ai...")
    headers = {
        'content-type': 'application/json',
        'x-api-key': os.getenv("DEEP_IMAGE_API_KEY") # Make sure to set this in your .env file
    }
    payload = {
        "enhancements": ["denoise", "deblur", "light"],
        "url": "https://deep-image.ai/api-example.png", # This is an example URL
        "width": 2000
    }
    response = requests.post('https://deep-image.ai/rest_api/process_result', headers=headers, json=payload)
    
    if response.status_code == 200:
        image_url = response.json().get('output_url') # Assuming the API returns the URL in 'output_url'
        image_path = image_url # Use the URL directly
        st.success("Image enhancement complete.")
    else:
        st.error(f"Image generation failed: {response.text}")
        image_url = "https://via.placeholder.com/512" # Placeholder on failure
        image_path = image_url


  # Audio Ad Generation
    st.info("Generating audio ad with ElevenLabs...")
    
    # Check if API key is available
    eleven_api_key = os.getenv("ELEVEN_API_KEY")
    voice_id = os.getenv("ELEVEN_VOICE_ID")
    
    if not eleven_api_key:
        st.warning("ELEVEN_API_KEY not found in environment variables. Skipping audio generation.")
        audio_url = None
    elif not voice_id:
        st.warning("ELEVEN_VOICE_ID not found in environment variables. Skipping audio generation.")
        audio_url = None
    else:
        try:
            client = ElevenLabs(api_key=eleven_api_key)
            
            # Generate audio bytes using the ElevenLabs API
            audio_stream = client.text_to_speech.convert(
                voice_id=voice_id,
                text=f"Listen to this amazing ad for {product}. {text_output.splitlines()[0]}",
                model_id="eleven_multilingual_v2"
            )

            # The result is a stream, so we need to concatenate the chunks to get the full audio bytes
            audio_bytes = b"".join(chunk for chunk in audio_stream)

            play(audio_bytes)
            # Optionally, save the audio to a file
            audio_url = "generated_audio.mp3"
            with open(audio_url, "wb") as f:
                f.write(audio_bytes)
            st.success("Audio generation complete.")
            
        except Exception as e:
            st.error(f"Audio generation failed: {str(e)}")
            st.info("Please check your ElevenLabs API key and voice ID.")
            audio_url = None


    st.subheader("📢 Ad Copy")
    st.write(text_output.split("\n")[0])

    st.subheader("📧 Email Campaign")
    st.write(text_output.split("\n")[1:3])

    st.subheader("📱 Social Media Posts")
    st.write(text_output.split("\n")[3:])

    st.subheader("🎨 Creative")
    st.image(image_url, caption="Generated Creative")

    if audio_url:
        st.subheader("🔊 Audio Ad")
        st.audio(audio_url)
    else:
        st.subheader("🔊 Audio Ad")
        st.info("Audio generation skipped due to API key issues.")

    # Save to DB
    data = {
        "product": product,
        "audience": audience,
        "ad_copy": text_output.split("\n")[0],
        "email": str(text_output.split("\n")[1:3]),
        "social": str(text_output.split("\n")[3:]),
        "image": image_url,
        "audio": audio_url or "N/A"
    }
    save_campaign(data)
    st.success("✅ Campaign saved to database")
