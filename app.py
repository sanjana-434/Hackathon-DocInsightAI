import streamlit as st
import requests

def main():
    st.set_page_config(page_title="Document Chat", page_icon="📚")
    st.title("Chat with Documents")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    with st.sidebar:
        files = st.file_uploader("Upload PDFs", accept_multiple_files=True, type=['pdf'])
        
        if st.button("Process"):
            if files:
                with st.spinner("Processing..."):
                    response = requests.post(
                        "http://localhost:8000/upload",
                        files=[('files', f) for f in files]
                    )
                    if response.ok:
                        st.success("✅ Ready to chat!")
                    else:
                        st.error("Processing failed")

    question = st.text_input("Ask about your documents:")
    
    if question:
        with st.spinner("Thinking..."):
            response = requests.post(
                "http://localhost:8000/chat",
                json={"question": question}
            )
            if response.ok:
                answer = response.json()["response"]
                st.session_state.chat_history.append((question, answer))

    for q, a in st.session_state.chat_history:
        st.write(f"Q: {q}")
        st.write(f"A: {a}")
        st.divider()

if __name__ == "__main__":
    main()