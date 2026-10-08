
import os
import time

import streamlit as st
from google import genai
from google.genai import types
from twilio.rest import Client

from prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
    SUMMARY_REQUEST_PROMPT,
)


st.set_page_config(
    page_title="NutriSnap AI",
    page_icon="🥗",
    layout="centered",
)


def get_secret(key, default=None):
    """Read a setting from Streamlit secrets or environment variables."""
    try:
        value = st.secrets.get(key, default)
    except Exception:
        value = default

    if not value:
        value = os.getenv(key, default)

    return value


GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
TWILIO_ACCOUNT_SID = get_secret("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = get_secret("TWILIO_AUTH_TOKEN")

# Must be the sender address shown in your Twilio Console.
TWILIO_WHATSAPP_FROM = get_secret(
    "TWILIO_WHATSAPP_NUMBER"
)

# Use a model ID currently available to your Gemini API key.
MODEL_NAME = "gemini-3.5-flash"


@st.cache_resource
def get_gemini_client(api_key):
    return genai.Client(api_key=api_key)


gemini_client = None
GEMINI_CONFIG_ERROR = None

if GEMINI_API_KEY:
    try:
        gemini_client = get_gemini_client(GEMINI_API_KEY)
    except Exception as exc:
        GEMINI_CONFIG_ERROR = str(exc)
else:
    GEMINI_CONFIG_ERROR = "GEMINI_API_KEY is missing."


twilio_client = None

if all(
    [
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN,
        TWILIO_WHATSAPP_FROM,
    ]
):
    try:
        twilio_client = Client(
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN,
        )
    except Exception as exc:
        print("Twilio client initialization error:", repr(exc))


def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])

        elif message["kind"] == "image":
            st.image(
                message["content"],
                use_container_width=True,
            )


def add_message(role, kind, content):
    message = {
        "role": role,
        "kind": kind,
        "content": content,
    }

    st.session_state.messages.append(message)
    render_message(message)



def ask_gemini(parts):
    for attempt in range(3):
        try:
            response = st.session_state.chat.send_message(parts)
            return response.text or "No response generated."

        except Exception as error:
            print("Gemini API error:", repr(error))

            error_text = str(error)

            if (
                ("503" in error_text or "UNAVAILABLE" in error_text)
                and attempt < 2
            ):
                time.sleep(2 ** (attempt + 1))
                continue

            st.error(f"Gemini API error: {error_text}")
            return None

    return None



def clean_whatsapp_text(text):
    if not text:
        return "No nutrition summary available."

    text = " ".join(text.split())

    if len(text) > 1500:
        text = text[:1497] + "..."

    return text


def send_whatsapp(to_number, user_name, summary):
    """Send the summary using the configured Twilio WhatsApp sender."""

    if twilio_client is None:
        return False, (
            "Twilio credentials or WhatsApp sender are not configured."
        )

    if not summary:
        return False, "No summary was generated. Please try again."

    # Avoid accidentally adding the WhatsApp prefix twice.
    recipient = to_number.strip()

    if recipient.startswith("whatsapp:"):
        recipient = recipient[len("whatsapp:"):]

    if not recipient.startswith("+"):
        return False, "The recipient number must include its country code."

    try:
        message = twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{recipient}",
            body=(
                f"🥗 NutriSnap AI summary for {user_name}\n\n"
                f"{clean_whatsapp_text(summary)}"
            ),
        )

        return True, message.sid

    except Exception as error:
        print("Twilio API error:", repr(error))
        return False, str(error)



if "messages" not in st.session_state:
    st.session_state.messages = []


if "onboarded" not in st.session_state:
    st.title("🥗 NutriSnap AI")
    st.caption("Snap it. Track it. Text yourself the results.")

    st.write(
        "Your AI nutrition buddy estimates calories and "
        "macronutrients from meal descriptions and photos."
    )

    if GEMINI_CONFIG_ERROR:
        st.warning(
            "Gemini API configuration is not ready. "
            "Check your API key and model configuration."
        )

    with st.form("onboarding_form"):
        name = st.text_input("Your name")

        whatsapp_number = st.text_input(
            "WhatsApp number (with country code)",
            placeholder="+91XXXXXXXXXX",
            help="Use the number registered with your Twilio Sandbox.",
        )

        submitted = st.form_submit_button(
            "Let's go 🚀",
            use_container_width=True,
        )

    if submitted:
        clean_name = name.strip()
        clean_number = whatsapp_number.strip()

        if not clean_name or not clean_number:
            st.warning("Please enter both your name and WhatsApp number.")

        elif (
            not clean_number.startswith("+")
            or not clean_number[1:].isdigit()
        ):
            st.warning(
                "Enter the number with country code, "
                "for example +919876543210."
            )

        elif gemini_client is None:
            st.error(
                "Gemini is not configured. Check GEMINI_API_KEY "
                "in .streamlit/secrets.toml."
            )

        else:
            try:
                chat = gemini_client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                    ),
                )

                st.session_state.name = clean_name
                st.session_state.whatsapp_number = clean_number
                st.session_state.chat = chat
                st.session_state.messages = []
                st.session_state.onboarded = True

                st.rerun()

            except Exception as exc:
                st.error(
                    "Could not initialize the Gemini chat. "
                    "Check the model ID, API key, and available quota."
                )
                st.caption(f"Technical details: {exc}")

    st.stop()


header_col, button_col = st.columns(
    [5, 2],
    vertical_alignment="center",
)

with header_col:
    st.title("🥗 NutriSnap AI")

with button_col:
    # One welcome message alone should not enable the button.
    user_has_chatted = any(
        message["role"] == "user"
        for message in st.session_state.messages
    )

    if st.button(
        "📤 Send to WhatsApp",
        disabled=not user_has_chatted,
        use_container_width=True,
    ):
        with st.spinner("Preparing your nutrition summary..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])

        if summary:
            success, info = send_whatsapp(
                st.session_state.whatsapp_number,
                st.session_state.name,
                summary,
            )

            if success:
                st.success("Sent! Check your WhatsApp 📲")
            else:
                st.error(f"Couldn't send the summary: {info}")


st.caption(
    f"Your personal nutrition buddy, {st.session_state.name}!"
)


if not st.session_state.messages:
    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(
            name=st.session_state.name
        ),
    )
else:
    for message in st.session_state.messages:
        render_message(message)


user_input = st.chat_input(
    "Ask a question, or attach a photo of your meal",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)


if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text.strip() if user_input.text else ""

    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()

        # Show the photo in the chat.
        add_message("user", "image", photo_bytes)

        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type,
            )
        )

    if text:
        add_message("user", "text", text)
        parts.append(text)

    elif photo is not None:
        parts.append(
            "Identify the visible meal and estimate its calories, "
            "protein, carbohydrates, and fat. State that the "
            "nutrition values are approximate."
        )

    if parts:
        with st.spinner("🥗 Analyzing your meal..."):
            answer = ask_gemini(parts)

        if answer:
            add_message("assistant", "text", answer)
