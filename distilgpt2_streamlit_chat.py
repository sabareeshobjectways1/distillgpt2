import streamlit as st

try:
    from transformers import pipeline, set_seed
except ImportError:
    st.error("Missing dependencies. Please run:\n\npip install streamlit transformers torch")
    st.stop()

# Page config
st.set_page_config(page_title="Chat with DistilGPT2", layout="centered")
st.title("💬 Chat with DistilGPT2")
st.caption("Powered by 🤗 Hugging Face Transformers — No API Keys Required")

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Load model only once
@st.cache_resource(show_spinner=True)
def load_model():
    generator = pipeline("text-generation", model="distilgpt2")
    set_seed(42)
    return generator

try:
    generator = load_model()
except Exception as e:
    st.error("🚨 Failed to load DistilGPT2 model.")
    st.exception(e)
    st.stop()

# Input
prompt = st.text_input("Your message:", placeholder="Type a message and hit Enter")

if prompt:
    with st.spinner("Generating response..."):
        try:
            output = generator(prompt, max_new_tokens=60, do_sample=True, temperature=0.7)[0]["generated_text"]
            st.session_state.chat_history.append(("🧑 You", prompt))
            st.session_state.chat_history.append(("🤖 DistilGPT2", output))
        except Exception as e:
            st.error("❌ Error during response generation.")
            st.exception(e)

# Display chat
st.markdown("### 🗨️ Conversation")
for sender, text in st.session_state.chat_history:
    st.markdown(f"**{sender}:** {text}")

# Clear button
if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = []
    
