import streamlit as st

# Page configuration
st.set_page_config(
    page_title="JARVIS AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Title
st.title("🤖 JARVIS AI Assistant")
st.subheader("Your Personal AI Assistant")

# Online status
st.success("🟢 JARVIS is Online")

st.divider()

# Sidebar
with st.sidebar:
    st.header("⚙️ JARVIS Controls")

    if st.button("🔄 Check Status", use_container_width=True):
        st.success("JARVIS is running!")

    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.messages = []

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
user_input = st.chat_input("Ask JARVIS something...")

if user_input:
    # Show user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.write(user_input)

    # Temporary response
    response = (
        "I'm JARVIS. Your AI assistant is online. "
        "My AI brain will be connected here next."
    )

    # Show JARVIS response
    with st.chat_message("assistant"):
        st.write(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

# Features
st.divider()

st.subheader("🚀 JARVIS Capabilities")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.info("🧠\n\nAI Brain")

with col2:
    st.info("🎙️\n\nVoice Assistant")

with col3:
    st.info("👁️\n\nComputer Vision")

with col4:
    st.info("⚙️\n\nAutomation")
