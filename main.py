import sys
from pathlib import Path

import streamlit as st


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =========================================================
# IMPORT JARVIS BRAIN
# =========================================================

try:
    from core.brain import ask_jarvis
    BRAIN_AVAILABLE = True
    BRAIN_ERROR = None

except Exception as error:
    BRAIN_AVAILABLE = False
    BRAIN_ERROR = str(error)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="JARVIS AI Assistant",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# HEADER
# =========================================================

st.title("🤖 JARVIS AI Assistant")

st.caption(
    "Your Personal AI Assistant"
)


if BRAIN_AVAILABLE:
    st.success("🟢 JARVIS is Online")
else:
    st.error("🔴 JARVIS Brain could not be loaded")


st.divider()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙️ JARVIS Status")

    if BRAIN_AVAILABLE:
        st.success("🧠 AI Brain: Ready")
    else:
        st.error("🧠 AI Brain: Error")

    st.success("🌤️ Weather: Ready")
    st.success("🧮 Calculator: Ready")
    st.success("💾 Memory: Ready")

    st.divider()

    if st.button(
        "🧹 Clear Chat",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()


# =========================================================
# ERROR INFORMATION
# =========================================================

if not BRAIN_AVAILABLE:

    st.warning(
        "JARVIS could not load the brain module."
    )

    st.code(
        BRAIN_ERROR,
        language="text"
    )

    st.stop()


# =========================================================
# CHAT HISTORY
# =========================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )


# =========================================================
# CHAT INPUT
# =========================================================

user_input = st.chat_input(
    "Ask JARVIS anything..."
)


# =========================================================
# PROCESS USER MESSAGE
# =========================================================

if user_input:

    # -----------------------------------------------------
    # USER MESSAGE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):

        st.write(user_input)


    # -----------------------------------------------------
    # JARVIS RESPONSE
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "🤖 JARVIS is thinking..."
        ):

            try:

                response = ask_jarvis(
                    user_input
                )

            except Exception as error:

                response = (
                    "Sorry, JARVIS encountered an error.\n\n"
                    f"Error: {error}"
                )

        st.write(response)


    # -----------------------------------------------------
    # SAVE RESPONSE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "JARVIS AI Assistant • Built with Python & Streamlit"
)


