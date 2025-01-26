# Code for PDF QnA
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Function to Extract Text from PDFs
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


# Function to Split Text into Chunks
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks


# Function to Generate Vector Store
def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")


# Function to Create Conversational Chain
def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context. Make sure to provide all the details. 
    If the answer is not in the provided context, just say, "Answer is not available in the context." 
    Do not provide a wrong answer.\n\n
    Context:\n{context}?\n
    Question:\n{question}\n

    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain


# Function to Handle User Input
def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain()

    response = chain.invoke(
        {"input_documents": docs, "question": user_question}, return_only_outputs=True
    )
    return response["output_text"]


# Function to Generate Quiz Prompt
def generate_quiz_prompt(context):
    poompt = '''
Can you give me 10 quiz questions based on {}, I want it in the following JSON format:
[
    {{
        "question": "(Question)",
        "options": ["A.option1", "B.option2", "C.option3", "D.option4"],
        "answer": "(Whole correct option)"
    }},
    ...
]
Each option should be labeled alphabetically, as shown in the example.
'''.format(context)
    return poompt


from AI.Que_gen import que_gen


def main():
    # Page Configurations
    st.set_page_config(page_title="Kairos", layout="wide")
    st.header("Welcome to AI-Powered Learning Companion - Kairos!")

    # Project Description
    st.markdown("""
    ## About Kairos:
    Kairos is an AI-powered educational tool designed to make learning easier and more interactive. 
    This platform allows you to:
    - **Upload PDF documents** and extract key insights.
    - **Generate customized quizzes** to test your knowledge on specific topics.
    - **Interact with a Q&A system** for detailed understanding of your content.
    - **Evaluate performance** through detailed report cards.

    With Kairos, enhance your learning experience using the power of AI and automation!
    """)

    # Sidebar for File Uploads
    with st.sidebar:
        st.title("Menu:")
        pdf_docs = st.file_uploader("Upload your PDF Files", accept_multiple_files=True)
        # Process button for handling uploads
        if st.button("Submit & Process"):
            if pdf_docs:
                with st.spinner("Processing..."):
                    raw_text = get_pdf_text(pdf_docs)
                    text_chunks = get_text_chunks(raw_text)
                    get_vector_store(text_chunks)
                    st.success("PDFs processed and indexed successfully!")
            else:
                st.warning("Please upload at least one PDF file before clicking Submit.")

    # Quiz Generation Section
    context = st.text_input("On what topic you want the quiz?")
    if context:
        prmt = generate_quiz_prompt(context)
        r_ques = user_input(prmt)
        que_gen(r_ques)
        st.success("Quiz questions generated successfully!")

    # Redirect to Quiz Preparation Page
    if st.button("Prepare Quiz"):
        st.write("Redirecting to the quiz logic...")  # Stub for redirection logic

    # Footer with Project Description
    st.markdown(
        """
        <div style="position: fixed; bottom: 20px; right: 20px; font-size: 12px; color: grey; text-align: right;">
            <b>About Kairos:</b> An AI-powered educational tool for PDF analysis, quiz generation, and enhanced learning.
        </div>
        """,
        unsafe_allow_html=True
    )


# Run the app
if __name__ == "__main__":
    main()
