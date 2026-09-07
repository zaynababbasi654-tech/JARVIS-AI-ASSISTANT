import streamlit as st
import sys
from pathlib import Path

# Project root ko Python path mein add karo
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.brain import ask_jarvis


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="JARVIS AI Assistant",
    page_icon="🤖",
    layout="wide"
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("🤖 JARVIS AI Assistant")
st.caption("Your Personal AI Assistant")

st.success("🟢 JARVIS is Online")

st.divider()


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.header("⚙️ JARVIS")

    st.write("System Status")

    st.success("🧠 AI Brain: Online")
    st.success("🌤️ Weather: Online")
    st.success("🧮 Calculator: Online")
    st.success("💾 Memory: Online")

    st.divider()

    if st.button(
        "🧹 Clear Chat",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()


# ---------------------------------------------------------
# CHAT MEMORY
# ---------------------------------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []


# ---------------------------------------------------------
# DISPLAY CHAT HISTORY
# ---------------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )


# ---------------------------------------------------------
# USER INPUT
# ---------------------------------------------------------

user_input = st.chat_input(
    "Ask JARVIS anything..."
)


if user_input:

    # User message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):

        st.write(user_input)


    # JARVIS response
    with st.chat_message("assistant"):

        with st.spinner(
            "JARVIS is thinking..."
        ):

            try:

                response = ask_jarvis(
                    user_input
                )

            except Exception as error:

                response = (
                    "Sorry, I encountered an error:\n\n"
                    f"{error}"
                )

        st.write(response)


    # Save response
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })


