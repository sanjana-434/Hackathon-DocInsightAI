import google.generativeai as genai
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import os
import io

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def process_pdf(files):
    text = ""
    for file in files:
        content = await file.read()
        pdf = PdfReader(io.BytesIO(content))
        for page in pdf.pages:
            text += page.extract_text()

    splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = splitter.split_text(text)
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    return vector_store

async def get_response(question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = vector_store.similarity_search(question)

    prompt = PromptTemplate(
        template="""Answer based on context. If answer isn't in context, say "Not found in documents."\n\nContext:\n{context}\nQuestion:\n{question}\n\nAnswer:""",
        input_variables=["context", "question"]
    )

    chain = load_qa_chain(
        ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3),
        chain_type="stuff",
        prompt=prompt
    )

    response = chain(
        {"input_documents": docs, "question": question},
        return_only_outputs=True
    )
    return response["output_text"]