import json
import smtplib
import time
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st
from google import genai
from google.genai import types

from prompts import SUMMARY_REQUEST_PROMPT, SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE

MODEL_NAME = st.secrets.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
st.set_page_config(page_title="StyleAI", page_icon="👗")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GMAIL_SENDER = st.secrets.get("GMAIL_SENDER", "")
GMAIL_APP_PASSWORD = st.secrets.get("GMAIL_APP_PASSWORD", "")


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()


def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])


def add_message(role, kind, content):
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])


def ask_gemini(parts):
    try:
        return st.session_state.chat.send_message(parts).text
    except Exception as error:
        # Automatic retry for temporary 503 / 429 server overload
        if any(err in str(error) for err in ["503", "UNAVAILABLE", "429"]):
            time.sleep(2)
            try:
                return st.session_state.chat.send_message(parts).text
            except Exception as retry_err:
                return f"The AI service is temporarily busy. Please try again: {retry_err}"
        return f"Sorry, something went wrong: {error}"


def send_email_smtp(to_email, user_name, summary):
    """
    Sends the summary directly to the user's email inbox using Gmail SMTP.
    """
    if not GMAIL_SENDER or not GMAIL_APP_PASSWORD:
        return False, "GMAIL_SENDER or GMAIL_APP_PASSWORD not set in secrets."

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"👗 StyleAI Outfit Plan for {user_name}"
        msg["From"] = f"StyleAI <{GMAIL_SENDER}>"
        msg["To"] = to_email

        plain_text = f"Hi {user_name}!\n\nHere is your StyleAI outfit summary:\n\n{summary}\n\nStay stylish,\nStyleAI"
        html_summary = summary.replace("\n", "<br>")
        html_text = f"""
        <html>
          <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #2d3748; background: #f7fafc; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0;">
              <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; color: #ffffff; text-align: center;">
                <h1 style="margin: 0; font-size: 22px;">👗 StyleAI Outfit Summary</h1>
                <p style="margin: 6px 0 0 0; opacity: 0.9; font-size: 14px;">Curated for {user_name}</p>
              </div>
              <div style="padding: 24px; font-size: 15px;">
                {html_summary}
              </div>
              <div style="background: #edf2f7; padding: 12px; text-align: center; font-size: 12px; color: #718096;">
                Delivered automatically by StyleAI
              </div>
            </div>
          </body>
        </html>
        """
        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        msg.attach(MIMEText(html_text, "html", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        return True, "Email sent successfully!"
    except Exception as error:
        return False, str(error)


# Step 1: onboarding
if "onboarded" not in st.session_state:
    st.title("👗 StyleAI")
    st.caption("Upload clothing. Get combinations. Text yourself the results.")
    with st.form("onboarding_form"):
        name = st.text_input("Your name")
        whatsapp_number = st.text_input(
            "WhatsApp number (with country code)",
            placeholder="+91XXXXXXXXXX",
            help="This is the phone number for your 1-click WhatsApp delivery.",
        )
        email = st.text_input(
            "Email address (optional for automated delivery)",
            placeholder="you@gmail.com",
            help="Your email to receive the summary directly in your inbox.",
        )
        submitted = st.form_submit_button("Let's go 🚀")
    if submitted:
        if not name.strip() or not whatsapp_number.strip():
            st.warning("Please fill in both your name and WhatsApp number.")
        else:
            st.session_state.name = name.strip()
            st.session_state.whatsapp_number = whatsapp_number.strip()
            st.session_state.email = email.strip()
            st.session_state.chat = gemini_client.chats.create(
                model=MODEL_NAME,
                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            )
            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()
    st.stop()

# Step 2: chat interface
header_col, button_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title("👗 StyleAI")

with button_col:
    if st.button("📤 Send Summary", use_container_width=True):
        if len(st.session_state.messages) <= 1:
            st.warning("Please describe or upload a clothing item first so StyleAI can summarize your outfits!")
        else:
            with st.spinner("Summarizing your outfits..."):
                summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
                st.session_state.summary = summary

            # 1. Automated Email via Gmail SMTP
            if st.session_state.email:
                if GMAIL_SENDER and GMAIL_APP_PASSWORD:
                    success_mail, info_mail = send_email_smtp(
                        st.session_state.email, st.session_state.name, summary
                    )
                    if success_mail:
                        st.success(f"Email sent automatically to {st.session_state.email}! 📬")
                    else:
                        st.warning(f"Email delivery note: {info_mail}")
            else:
                st.info("Summary ready! You can also share it to your device below.")

st.caption(
    f"Logged in as {st.session_state.name} • Phone: {st.session_state.whatsapp_number}"
    + (f" • Email: {st.session_state.email}" if st.session_state.get("email") else "")
)

# Send directly to user's device (WhatsApp, Telegram, Email)
if "summary" in st.session_state and st.session_state.summary:
    summary_text = st.session_state.summary
    encoded_text = urllib.parse.quote(
        f"👗 StyleAI Summary for {st.session_state.name} 👗\n\n{summary_text}"
    )
    clean_digits = "".join(filter(str.isdigit, st.session_state.whatsapp_number))

    wa_url = f"https://wa.me/{clean_digits}?text={encoded_text}"
    tg_url = f"https://t.me/share/url?text={encoded_text}"
    email_target = st.session_state.get("email", "")
    mail_url = f"mailto:{email_target}?subject=StyleAI%20Outfit%20Summary&body={encoded_text}"

    with st.expander("📲 Send Summary Directly to Your Device (100% Free)", expanded=True):
        st.markdown(summary_text)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.link_button("💬 WhatsApp", wa_url, use_container_width=True)
        with c2:
            st.link_button("✈️ Telegram", tg_url, use_container_width=True)
        with c3:
            st.link_button("📧 Email App", mail_url, use_container_width=True)

if not st.session_state.messages:
    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name),
    )
else:
    for message in st.session_state.messages:
        render_message(message)

user_input = st.chat_input(
    "Describe an item or attach a clothing photo...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))
    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append(
            "Analyze this clothing item and suggest 3 practical outfit combinations."
        )

    with st.spinner("Styling your look..."):
        answer = ask_gemini(parts)
    add_message("assistant", "text", answer)