# 👗 StyleAI

StyleAI is an AI-powered personal fashion assistant built with Streamlit and Google Gemini. Users can upload a clothing photo or describe an item, receive smart styling combinations and occasion-based outfit ideas, and automatically send a complete outfit summary directly to their email inbox and device (WhatsApp / Telegram).

---

## 🌟 Features

- **Multimodal Visual Analysis:** Upload clothing photos (PNG, JPG, WEBP) analyzed via Gemini vision.
- **Interactive Styling Chat:** Chat naturally about colors, layering, footwear, and accessories.
- **Automated Email Delivery:** Directly delivers a formatted HTML outfit summary to the user's email inbox via Gmail SMTP.
- **1-Click Device Sharing:** 100% free instant links to send or save your summary in WhatsApp (`wa.me`) or Telegram.
- **Secure Secrets:** API keys and sensitive credentials stored safely in Streamlit secrets.

---

## 📁 Project Structure

```text
styleai/
├── app.py                     # Main Streamlit chat application & delivery logic
├── prompts.py                 # System persona and prompt instructions
├── requirements.txt           # Minimal dependencies (streamlit, google-genai)
├── README.md                  # Documentation and setup guide
├── .gitignore                 # Keeps secrets.toml and venv out of Git
└── .streamlit/
    ├── secrets.toml.example   # Safe template to track in GitHub
    └── secrets.toml           # Real private keys (IGNORED by Git - DO NOT COMMIT)
```

---

## 🚀 How to Run Locally

### 1. Prerequisites
- Python 3.9 or newer installed.
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com).

### 2. Set Up Virtual Environment

**Windows PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Secrets
Create your local secrets file from the template:
```bash
# Windows PowerShell
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml

# macOS / Linux
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Open `.streamlit/secrets.toml` and fill in your keys:
```toml
# Google AI Studio
GEMINI_API_KEY = "your-gemini-api-key-here"
GEMINI_MODEL = "gemini-3.5-flash-lite"

# Automated Gmail SMTP (Optional)
GMAIL_SENDER = "your-email@gmail.com"
GMAIL_APP_PASSWORD = "your-16-char-app-password"
```

*(To get a Gmail App Password: Google Account > Security > 2-Step Verification > App Passwords).*

### 5. Start the App
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## ⚠️ Git & Security Note

Never commit `.streamlit/secrets.toml`. Only `.streamlit/secrets.toml.example` should be tracked in Git.
To verify before pushing:
```bash
git status
```
Ensure `.streamlit/secrets.toml` is never listed under changes or staged files.
