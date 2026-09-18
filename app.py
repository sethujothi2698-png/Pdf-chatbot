import streamlit as st
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

st.set_page_config(page_title="PDF Chatbot", layout="centered")
st.title("📄 Chat with your PDF")

api_key = st.sidebar.text_input("Enter Google Gemini API Key:", type="password")

uploaded_file = st.file_uploader("Upload your PDF file", type=["pdf"])

if uploaded_file and api_key:
    # 1. Read PDF text
    pdf_reader = PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted

    # 2. Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = text_splitter.split_text(text)

    # 3. Create Vector DB
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    vector_store = Chroma.from_texts(chunks, embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # 4. Prompt & LLM Chain Setup
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)

    system_prompt = (
        "You are an assistant for answering questions based on the uploaded document.\n"
        "Use the following retrieved context to answer the question.\n"
        "If the answer is not in the context, say that you don't know based on the PDF.\n\n"
        "{context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    # 5. User Chat Input
    user_query = st.chat_input("Ask anything from this PDF...")
    if user_query:
        with st.spinner("Analyzing PDF..."):
            response = rag_chain.invoke({"input": user_query})
            st.write("**Answer:**")
            st.write(response["answer"])
          
