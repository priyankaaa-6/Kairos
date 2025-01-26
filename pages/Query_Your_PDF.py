# Main file for the application
import streamlit as st  # Framework for creating web applications
from PyPDF2 import PdfReader  # Library for reading PDF files
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Utility for splitting text into manageable chunks
import os  # Provides operating system interaction
from langchain_google_genai import GoogleGenerativeAIEmbeddings  # Handles Google Generative AI embeddings
import google.generativeai as genai  # Library to interact with Google Generative AI
from langchain.vectorstores import FAISS  # Vector database for storing and searching embeddings
from langchain_google_genai import ChatGoogleGenerativeAI  # For conversational AI interactions with Google Generative AI
from langchain.chains.question_answering import load_qa_chain  # Loads a predefined chain for question-answering tasks
from langchain.prompts import PromptTemplate  # Defines prompt templates for interacting with AI
from dotenv import load_dotenv  # Library to load environment variables from a `.env` file

# Load environment variables
load_dotenv()
os.getenv("GOOGLE_API_KEY")  # Fetches the Google API key from environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Configures the Google Generative AI API

# Page Configurations
st.set_page_config(page_title="Kairos", layout="wide")  # Sets the page title and layout configuration
st.header("AI-Powered Learning Companion - Kairos!")  # App header

# Function to extract text from uploaded PDF files
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:  # Iterate through the list of uploaded PDF files
        pdf_reader = PdfReader(pdf)  # Initialize PDF reader
        for page in pdf_reader.pages:  # Extract text from each page
            text += page.extract_text()
    return text  # Return the combined text from all PDFs

# Function to split text into smaller, manageable chunks
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)  # Configures chunking parameters
    chunks = text_splitter.split_text(text)  # Splits the text into chunks
    return chunks  # Returns the text chunks

# Function to generate and save vector embeddings for the text chunks
def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")  # Initializes embeddings model
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)  # Generates a vector store from text chunks
    vector_store.save_local("faiss_index")  # Saves the vector store locally

# Function to create the conversational AI chain
def get_conversational_chain():
    # Defines the template for conversational prompts
    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details. If the answer is not in
    provided context, just say, "answer is not available in the context", don't provide the wrong answer.\n\n
    Context:\n {context}\n
    Question:\n{question}\n
    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)  # Configures the conversational AI model
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])  # Prepares the prompt template
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)  # Creates the question-answering chain
    return chain  # Returns the chain for use

# Function to handle user input and generate a response
def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")  # Initializes embeddings
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)  # Loads the vector store
    docs = new_db.similarity_search(user_question)  # Searches for relevant documents using embeddings

    chain = get_conversational_chain()  # Creates the conversational chain
    response = chain.invoke({"input_documents": docs, "question": user_question}, return_only_outputs=True)  # Queries the AI chain
    print(response)  # Debug: Prints the response to the console
    st.write("Reply: ", response["output_text"])  # Displays the AI's response on the Streamlit app

# Main function to handle the application logic
def main():
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
    user_question = st.text_input("Ask a Question from the PDF Files")  # Input field for the user's question

    if user_question:  # If a question is provided
        user_input(user_question)  # Processes the user's question

    # Sidebar configuration for uploading PDF files
    with st.sidebar:
        st.title("Menu:")  # Sidebar title
        pdf_docs = st.file_uploader("Upload your PDF Files and Click on the Submit & Process Button", accept_multiple_files=True)  # File upload field
        if st.button("Submit & Process"):  # Button to process the uploaded files
            with st.spinner("Processing..."):  # Displays a spinner while processing
                raw_text = get_pdf_text(pdf_docs)  # Extracts text from the uploaded PDFs
                text_chunks = get_text_chunks(raw_text)  # Splits the text into chunks
                get_vector_store(text_chunks)  # Creates and saves the vector embeddings
                st.success("Done")  # Displays success message after processing
                
        # Footer with Project Description
    st.markdown(
        """
        <div style="position: fixed; bottom: 20px; right: 20px; font-size: 12px; color: grey; text-align: right;">
            <b>About Kairos:</b> An AI-powered educational tool for PDF analysis, quiz generation, and enhanced learning.
        </div>
        """,
        unsafe_allow_html=True
    )

# Entry point for the application
if __name__ == "__main__":
    main()  # Runs the main function
