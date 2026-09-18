import os
import io
import requests
import streamlit as st
from PIL import Image
from groq import Groq
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# Configuration & Page Setup
# -----------------------------------------------------------------------------
load_dotenv()  # Load environment variables from .env file

st.set_page_config(
    page_title="VisionCraft AI | Safe Image Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Blocked NSFW/Safety terms for initial client-side filtering
BLOCKED_KEYWORDS = [
    "nsfw", "nude", "nudity", "naked", "porn", "xxx", "explicit", 
    "gore", "blood", "decapitation", "sex", "erotic"
]

# -----------------------------------------------------------------------------
# Custom Styling (CSS)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Main Background & Text Styling */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
    }
    
    /* Header Container */
    .header-title {
        font-family: 'Inter', system-ui, sans-serif;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.2rem !important;
        margin-bottom: 0.2rem;
        letter-spacing: -1px;
    }
    
    .header-subtitle {
        color: #94a3b8;
        font-size: 1.15rem;
        margin-bottom: 2rem;
    }

    /* Primary Interactive Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.39);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.5);
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
    }

    /* Hide Streamlit Native Footers */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# API Key Management (Security Focus)
# -----------------------------------------------------------------------------
groq_api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)

# Sidebar - Settings & Security Options
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/paint-palette.png", width=64)
    st.title("Settings & Security")
    st.markdown("---")
    
    if not groq_api_key:
        st.warning("🔑 No API Key found in `.env`.")
        groq_api_key = st.text_input(
            "Enter Groq API Key:",
            type="password",
            help="Your API key stays securely in session memory and is never stored on a server."
        )
    else:
        st.success("🔒 Groq API Key loaded securely.")
        
    st.markdown("---")
    st.subheader("Rendering Parameters")
    
    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        ["1024x1024 (Square)", "1280x720 (Landscape)", "720x1280 (Portrait)"],
        index=0
    )
    
    enhance_prompt = st.toggle(
        "Magic Enhance & Moderation (Groq)",
        value=True,
        help="Uses Groq Llama 3 to sanitize unsafe prompts and expand them into high-quality visual art prompts."
    )
    
    seed = st.number_input("Seed (For reproducibility)", min_value=0, max_value=999999, value=42)

# Extract dimensions
dim_str = aspect_ratio.split(" ")[0]
width, height = map(int, dim_str.split("x"))

# Initialize Groq Client
client = None
if groq_api_key:
    try:
        client = Groq(api_key=groq_api_key)
    except Exception as e:
        st.sidebar.error(f"Initialization error: {e}")

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def enhance_and_sanitize_prompt(user_prompt: str) -> str:
    """Uses Groq to sanitize unsafe prompts and enhance artistic detail."""
    if not client:
        return user_prompt
    
    system_instruction = (
        "You are an expert AI safety and prompt engineering assistant. "
        "Expand the user prompt into a vivid, descriptive artistic image prompt. "
        "SAFETY MANDATE: If the user prompt contains requests for NSFW, explicit content, nudity, "
        "excessive violence, or illegal material, you MUST sanitize and convert it into a safe, "
        "family-friendly, PG-rated visual concept. "
        "Return ONLY the refined safe prompt text, with no explanations or preamble."
    )
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.6,
            max_tokens=250,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.warning(f"Could not perform Groq safety check/enhancement: {e}")
        return user_prompt


def generate_image(prompt: str, w: int, h: int, seed_val: int):
    """Fetches image with safety parameters appended to request."""
    formatted_prompt = requests.utils.quote(prompt)
    # safe=true requests server-side content safety enforcement
    url = f"https://image.pollinations.ai/prompt/{formatted_prompt}?width={w}&height={h}&seed={seed_val}&nologo=true&safe=true&model=flux"
    
    response = requests.get(url, timeout=45)
    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content))
    else:
        raise Exception(f"Image server responded with status code {response.status_code}")

# -----------------------------------------------------------------------------
# Main Application UI
# -----------------------------------------------------------------------------
st.markdown('<div class="header-title">VisionCraft AI</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Turn your imagination into breathtaking visual art using Groq & Flux with safety guardrails.</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 1. Enter Your Idea")
    user_prompt = st.text_area(
        "Prompt Input",
        placeholder="e.g., A futuristic cyberpunk owl perched on a neon glowing tree...",
        height=160,
        label_visibility="collapsed"
    )
    
    generate_btn = st.button("✨ Generate Artwork")

with col2:
    st.markdown("### 2. Live Canvas")
    image_placeholder = st.empty()
    image_placeholder.info("👈 Enter a prompt and click **Generate Artwork** to produce an image.")

# -----------------------------------------------------------------------------
# Execution Workflow
# -----------------------------------------------------------------------------
if generate_btn:
    prompt_lower = user_prompt.lower()
    
    # Layer 1 Guardrail: Client-Side Keyword Filter
    if any(keyword in prompt_lower for keyword in BLOCKED_KEYWORDS):
        st.error("⚠️ Prompt rejected: Contains blocked keywords or explicit content request. Please keep prompts family-friendly.")
    elif not user_prompt.strip():
        st.error("Please enter a text prompt first.")
    else:
        final_prompt = user_prompt
        
        # Layer 2 Guardrail: Groq System Prompt Moderation & Expansion
        if enhance_prompt:
            if not groq_api_key:
                st.error("Groq API key is missing. Add it to `.env` or the sidebar to enable safety moderation.")
                st.stop()
            
            with st.status("🛡️ Safety moderation & prompt enhancement in progress...", expanded=False) as status:
                final_prompt = enhance_and_sanitize_prompt(user_prompt)
                status.update(label="✨ Prompt Sanitized & Enhanced!", state="complete")
            
            st.caption(f"**Sanitized Visual Prompt:** _{final_prompt}_")

        # Layer 3 Guardrail: Server API Safe Flag
        with st.spinner("🎨 Rendering high-resolution artwork..."):
            try:
                img = generate_image(final_prompt, width, height, seed)
                
                with col2:
                    image_placeholder.image(img, use_column_width=True, caption=user_prompt)
                    
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    
                    st.download_button(
                        label="📥 Download High-Res Image (PNG)",
                        data=byte_im,
                        file_name="visioncraft_artwork.png",
                        mime="image/png",
                    )
                st.toast("Artwork created successfully!", icon="🎨")
                
            except Exception as err:
                st.error(f"Generation error: {err}")