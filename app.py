import streamlit as st
from pypdf import PdfReader
import google.generativeai as genai

st.set_page_config(page_title="PDF Chatbot", page_icon="📄", layout="centered")
st.title("📄 Chat with your PDF")

api_key = st.sidebar.text_input("Enter Google Gemini API Key:", type="password")

uploaded_file = st.file_uploader("Upload your PDF file", type=["pdf"])

if "messages" not in st.session_state:
    st.session_state.messages = []

pdf_text = ""
if uploaded_file:
    pdf_reader = PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            pdf_text += extracted
    st.success("PDF uploaded & analysed successfully!")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask any question from this PDF..."):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar!")
    elif not uploaded_file:
        st.error("Please upload a PDF first!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-3.6-flash")

            full_prompt = f"Context from PDF:\n{pdf_text}\n\nQuestion:\n{prompt}\n\nAnswer strictly using the provided context."

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = model.generate_content(full_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {e}")
