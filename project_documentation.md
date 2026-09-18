# 🎨 VisionCraft AI — Image Generator

A sleek, modern Streamlit web application that uses **Groq (Llama 3)** for AI prompt optimization and safety moderation, coupled with high-speed diffusion models to generate high-resolution images from text prompts.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red)
![Groq API](https://img.shields.io/badge/Groq-Llama%203.1-orange)

---

## ✨ Features

- **🧠 Groq-Powered Magic Enhance:** Automatically expands basic prompts into rich, detailed art descriptions (lighting, style, mood, composition).
- **🛡️ Multi-Layer NSFW Guardrails:**
  - *Layer 1:* Client-side keyword filter blocks sensitive terms before processing.
  - *Layer 2:* Groq Llama 3 acts as an AI content moderator to sanitize unsafe inputs into family-friendly visual concepts.
  - *Layer 3:* Endpoint-level query filtering and robust exception handling.
- **⚡ Automatic Fallback Engine:** Prevents HTTP 500 crashes by automatically falling back to alternative render pipelines if a server node is congested.
- **🎨 Custom Visual Controls:** Choose custom aspect ratios (Square, Landscape, Portrait) and random seeds for reproducible image outcomes.
- **🔒 API Key Security:** Securely handles API keys via environment variables (`.env`) or Streamlit secrets—keys are never stored or logged.
- **📥 One-Click Export:** Download generated high-resolution artwork directly in `.png` format.

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/visioncraft-ai.git
cd visioncraft-ai
```

### 2. Install Dependencies
Ensure you have Python 3.9+ installed, then run:
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Open `.env` and insert your Groq API key:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```
> *(You can obtain a free Groq API key from the [Groq Console](https://console.groq.com/).)*

---

## 🚀 Running the Application

Launch the Streamlit app locally with:
```bash
streamlit run app.py
```

The web app will automatically open in your default browser at `http://localhost:8501`.

---

## 📁 Project Structure

```text
├── app.py              # Main Streamlit application with UI, Groq LLM logic, & API calls
├── requirements.txt    # Python package dependencies
├── .env.example        # Environment file template for API keys
└── README.md           # Project documentation
```

---

## 📦 Dependencies

- **streamlit** — Web interface framework
- **groq** — Groq API SDK for fast Llama-3 inference
- **requests** — HTTP library for fetching image outputs
- **pillow (PIL)** — Python Imaging Library for processing rendered images
- **python-dotenv** — Secure environment variable management

---

## 🌐 Deploying to Streamlit Cloud

1. Push your repository to **GitHub**.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and connect your repository.
3. Select `app.py` as your main file path.
4. Go to **Advanced Settings -> Secrets** in Streamlit Cloud and add your Groq key:
   ```toml
   GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
   ```
5. Click **Deploy**!

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).