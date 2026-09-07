import sys
from pathlib import Path

import streamlit as st


# =========================================================
# FIND PROJECT ROOT
# =========================================================

CURRENT_FILE = Path(__file__).resolve()

PROJECT_ROOT = CURRENT_FILE.parent.parent
CORE_DIR = PROJECT_ROOT / "core"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(CORE_DIR))


# =========================================================
# LOAD JARVIS BRAIN
# =========================================================

try:
    from brain import ask_jarvis

    BRAIN_AVAILABLE = True
    BRAIN_ERROR = None

except Exception as error:

    BRAIN_AVAILABLE = False
    BRAIN_ERROR = str(error)


# =========================================================
# STREAMLIT CONFIG
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

st.write(
    "Your Personal AI Assistant"
)


if BRAIN_AVAILABLE:

    st.success(
        "🟢 JARVIS is Online"
    )

else:

    st.error(
        "🔴 JARVIS Brain Error"
    )


st.divider()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙️ JARVIS System")

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
# BRAIN ERROR
# =========================================================

if not BRAIN_AVAILABLE:

    st.warning(
        "JARVIS could not load the Brain module."
    )

    st.code(
        BRAIN_ERROR,
        language="text"
    )

    st.stop()


# =========================================================
# CHAT MEMORY
# =========================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# =========================================================
# SHOW CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.write(
            message["content"]
        )


# =========================================================
# USER INPUT
# =========================================================

user_input = st.chat_input(
    "Ask JARVIS anything..."
)


# =========================================================
# JARVIS PROCESSING
# =========================================================

if user_input:

    # User message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):

        st.write(user_input)


    # JARVIS response
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
                    "JARVIS encountered an error:\n\n"
                    + str(error)
                )

        st.write(response)


    # Save response
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
    "JARVIS AI Assistant • Python • Streamlit"
)


