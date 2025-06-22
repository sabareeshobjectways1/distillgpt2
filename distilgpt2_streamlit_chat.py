import os
import subprocess
import streamlit as st

# Ensure dependencies are available
try:
    import torch
    import transformers
except ImportError:
    with st.spinner("Installing dependencies..."):
        subprocess.check_call(["pip", "install", "torch", "transformers", "streamlit"])
    import torch
    import transformers

from transformers import pipeline, set_seed

# Page config
st.set_page_config(page_title="Chat with DistilGPT2", layout="centered")
st.title("ðŸ’¬ Chat with DistilGPT2")
st.caption("Powered by ðŸ¤— Hugging Face Transformers â€” Local, Free, No API Keys")

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Load model (cached)
@st.cache_resource(show_spinner=True)
def load_model():
    generator = pipeline("text-generation", model="distilgpt2")
    set_seed(42)
    return generator

try:
    generator = load_model()
except Exception as e:
    st.error("ðŸš¨ Failed to load model. Try running locally or check system compatibility.")
    st.exception(e)
    st.stop()

# User prompt
prompt = st.text_input("Your message:", key="user_input", placeholder="Type a message and hit Enter")

# Handle response
if prompt:
    with st.spinner("Generating response..."):
        try:
            response = generator(prompt, max_new_tokens=60, do_sample=True, temperature=0.7)[0]["generated_text"]
            st.session_state.chat_history.append(("ðŸ§‘ You", prompt))
            st.session_state.chat_history.append(("ðŸ¤– DistilGPT2", response))
        except Exception as e:
            st.error("âŒ Error during generation.")
            st.exception(e)

# Display history
st.markdown("### ðŸ—¨ï¸ Conversation")
for sender, message in st.session_state.chat_history:
    st.markdown(f"**{sender}:** {message}")

# Clear chat
if st.button("ðŸ§¹ Clear Chat"):
    st.session_state.chat_history = []
