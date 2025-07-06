import streamlit as st
import requests
from chat_model import process_chat

API_url = "http://127.0.0.1:5000"


def show_chat():
    st.title("💬 Flight Assistant Chat")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask about flights...")

    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    res = requests.post(f"{API_url}/chat", json={"message": user_input})
                    response = res.json()["response"]
                except Exception as e:
                    response = f"❌ Error: {str(e)}"

                st.text(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
