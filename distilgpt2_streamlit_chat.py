import os
import subprocess
import streamlit as st

# Auto-install dependencies
try:
    import transformers
except ImportError:
    with st.spinner("Installing dependencies..."):
        subprocess.check_call(["pip", "install", "transformers", "streamlit"])

from transformers import pipeline, set_seed

# Set page config
st.set_page_config(page_title="Chat with DistilGPT2", layout="centered")
st.title("💬 Chat with DistilGPT2")
st.caption("Powered by 🤗 Hugging Face Transformers — Local, Free, No API Keys")

# Set up session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Load model (only once)
@st.cache_resource
def load_model():
    with st.spinner("Loading model... (this may take a moment)"):
        gen_pipeline = pipeline("text-generation", model="distilgpt2")
        set_seed(42)
        return gen_pipeline

generator = load_model()

# User input
prompt = st.text_input("Your message:", key="user_input", placeholder="Type a message and hit Enter")

# When user sends message
if prompt:
    with st.spinner("Generating response..."):
        response = generator(prompt, max_new_tokens=60, do_sample=True, temperature=0.7)[0]["generated_text"]

    # Store in chat history
    st.session_state.chat_history.append(("🧑 You", prompt))
    st.session_state.chat_history.append(("🤖 DistilGPT2", response))

# Display chat history
st.markdown("### 🗨️ Conversation")
for sender, message in st.session_state.chat_history:
    st.markdown(f"**{sender}:** {message}")

# Clear button
if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = []
