import os
import io
import urllib.parse
import requests
import streamlit as st
from PIL import Image
from groq import Groq
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# Configuration & Page Setup
# -----------------------------------------------------------------------------
load_dotenv()

st.set_page_config(
    page_title="Pro-Generator AI | Image Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (CSS)
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    .header-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        margin-bottom: 0.2rem;
    }
    .header-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 0.6rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.39);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.5);
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Guardrails & Safety Settings
# -----------------------------------------------------------------------------
RESTRICTED_KEYWORDS = [
    "nsfw", "nude", "nudity", "naked", "porn", "explicit", "gore", 
    "blood", "erotic", "sex", "breast", "genitals"
]

def check_content_safety(prompt: str) -> bool:
    prompt_lower = prompt.lower()
    return not any(keyword in prompt_lower for keyword in RESTRICTED_KEYWORDS)

# -----------------------------------------------------------------------------
# API Key Management
# -----------------------------------------------------------------------------
groq_api_key = os.getenv("GROQ_API_KEY")

with st.sidebar:
    st.title("Pro-Generator AI")
    st.markdown("---")
    
    if not groq_api_key:
        st.warning("🔑 No API Key found in `.env`.")
        groq_api_key = st.text_input(
            "Enter Groq API Key:",
            type="password",
            help="Your API key is used strictly in session memory and is never saved."
        )
    else:
        st.success("🔒 Groq API Key loaded securely.")
        
    st.markdown("---")
    st.subheader("Generation Settings")
    
    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        ["1024x1024 (Square)", "1280x720 (Landscape)", "720x1280 (Portrait)"],
        index=0
    )
    
    enhance_prompt = st.toggle(
        "Magic Enhance (Groq LLM)",
        value=True,
        help="Use Groq to refine and enrich your text into an artistic prompt."
    )
    
    seed = st.number_input("Seed (Optional)", min_value=0, max_value=999999, value=42)

dimensions = aspect_ratio.split(" ")[0].split("x")
width, height = int(dimensions[0]), int(dimensions[1])

client = None
if groq_api_key:
    try:
        client = Groq(api_key=groq_api_key)
    except Exception as e:
        st.sidebar.error(f"Failed to initialize Groq client: {e}")

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def enhance_prompt_with_groq(user_prompt: str) -> str:
    if not client:
        return user_prompt
    
    system_instruction = (
        "You are an expert, safety-conscious AI image prompt engineer. "
        "Expand the user input into a rich, photorealistic, descriptive image prompt with lighting and art direction details. "
        "CRITICAL SAFETY RULE: If the prompt contains explicit, nude, violent, or illegal elements, "
        "completely sanitize and rephrase it into a safe, artistic, family-friendly prompt. "
        "Return ONLY the refined safe prompt text."
    )
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.6,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.warning(f"Could not reach Groq LLM: {e}")
        return user_prompt


def generate_image(prompt: str, w: int, h: int, seed_val: int):
    encoded_prompt = urllib.parse.quote(prompt)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    primary_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={w}&height={h}&seed={seed_val}&nologo=true&model=flux"
    fallback_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={w}&height={h}&seed={seed_val}&nologo=true"
    
    try:
        response = requests.get(primary_url, headers=headers, timeout=25)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            fallback_resp = requests.get(fallback_url, headers=headers, timeout=25)
            if fallback_resp.status_code == 200:
                return Image.open(io.BytesIO(fallback_resp.content))
            else:
                raise Exception(f"Image server responded with status code {response.status_code}")
    except Exception as e:
        raise Exception(f"{e}")

# -----------------------------------------------------------------------------
# Main Application UI
# -----------------------------------------------------------------------------
st.markdown('<div class="header-title">Pro-Generator AI</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">High-performance AI visual creation suite powered by Groq & Flux.</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("1. Enter Your Visual Description")
    user_prompt = st.text_area(
        "Prompt Input",
        placeholder="e.g., A white-haired elf girl with royal garments sitting on a crystalline throne, cinematic lighting...",
        height=140,
        label_visibility="collapsed"
    )
    
    generate_btn = st.button("✨ Generate Artwork")

with col2:
    st.subheader("2. Visual Canvas")
    image_placeholder = st.empty()
    image_placeholder.info("👈 Enter a prompt and click Generate to create artwork.")

# -----------------------------------------------------------------------------
# Execution Workflow
# -----------------------------------------------------------------------------
if generate_btn:
    if not user_prompt.strip():
        st.error("Please enter a prompt before generating.")
    elif not check_content_safety(user_prompt):
        st.error("⚠️ Prompt contains restricted keywords. Please modify your description.")
    else:
        final_prompt = user_prompt
        
        if enhance_prompt:
            if not groq_api_key:
                st.error("Groq API Key is missing. Please add it to your `.env` file or sidebar.")
                st.stop()
                
            with st.status("🧠 Optimizing prompt with Groq...", expanded=False) as status:
                final_prompt = enhance_prompt_with_groq(user_prompt)
                status.update(label="✨ Prompt optimized successfully!", state="complete")
            
            st.caption(f"**Sanitized Visual Prompt:** _{final_prompt}_")

        with st.spinner("🎨 Rendering image..."):
            try:
                img = generate_image(final_prompt, width, height, seed)
                
                with col2:
                    image_placeholder.image(img, use_container_width=True, caption=user_prompt)
                    
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="📥 Download High-Res PNG",
                        data=byte_im,
                        file_name="pro_generator_artwork.png",
                        mime="image/png",
                    )
                st.toast("Image generated successfully!", icon="🎉")
                
            except Exception as err:
                st.error(f"Generation error: {err}")
