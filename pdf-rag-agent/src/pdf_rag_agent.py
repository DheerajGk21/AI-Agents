import shutil
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
import setup as config

# ============================================================
# LOAD the PDF document (knowledge source)
# ============================================================

def load_pdf():
    print("\n\n Loading the PDF document...")

    loader = PyPDFLoader(config.DOCUMENT_PATH)
    documents = loader.load()

    print(f"Loaded {len(documents)} pages.")

    return documents


# ============================================================
# Splitting and creating text chunks
# ============================================================

def split_documents(documents):
    print("Splitting the documents and creating text chunks...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP
    )

    chunks = text_splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    return chunks


# ============================================================
# CREATE EMBEDDINGS & SAVE IN VECTOR DATABASE | Convert the text chunks into vector co-ordinate embeddings and save locally
# ============================================================

def create_vector_database(chunks):
    print("Creating vector database...")

    # Delete previous vector database
    if os.path.exists(config.VECTOR_DB_PATH):
        shutil.rmtree(config.VECTOR_DB_PATH)

    # Embedding model
    embeddings = GoogleGenerativeAIEmbeddings(
        model=config.EMBEDDING_MODEL, google_api_key=config.GOOGLE_API_KEY
    )

    # Embedding chunks to vector data and Saving data locally
    vector_db = Chroma.from_documents(
        documents=chunks, embedding=embeddings, persist_directory=config.VECTOR_DB_PATH
    )

    print("Vector database and embeddings created.")

    return vector_db


# ============================================================
# CREATE RETRIEVER | Retrives "k" most-relevant chunks related to user input
# ============================================================

def create_retriever(vector_db):
    return vector_db.as_retriever(search_kwargs={"k": config.RETRIEVAL_COUNT})


# ============================================================
# CREATE PROMPT | Template indicating rules or system instructions to LLM
# ============================================================

def create_prompt():
    return PromptTemplate.from_template(config.SYSTEM_INSTRUCTIONS)


# ============================================================
# FORMAT RETRIEVED DOCUMENTS | Join the "k" most relevant data-chunks retrieved for user query
# ============================================================

def format_documents(documents):
    return "\n\n".join(document.page_content for document in documents)


# ============================================================
# ASK QUESTION | For user query, retrieve relevant chunks and pass them to LLM
# ============================================================

def ask_question(question, retriever, prompt, llm):

    # Step 1: Retrieve relevant chunks
    documents = retriever.invoke(question)

    # Step 2: Convert chunks into text
    context = format_documents(documents)

    # Step 3: Create the final prompt for LLM
    final_prompt = prompt.format(context=context, question=question)

    # Step 4: Send prompt to Gemini
    response = llm.invoke(final_prompt)

    # Step 5: Extract answer
    if isinstance(response.content, list):
        return response.content[0]["text"]

    return response.content


# ============================================================
# CREATE LLM | Create a LLM model to interact with use and process Agumented Data
# ============================================================

def create_llm():
    return ChatGoogleGenerativeAI(
        model=config.LLM_MODEL, temperature=0, google_api_key=config.GOOGLE_API_KEY
    )


# ============================================================
# INITIALIZE RAG SYSTEM
# ============================================================

def create_rag_system():
    documents = load_pdf()
    chunks = split_documents(documents)
    vector_db = create_vector_database(chunks)
    retriever = create_retriever(vector_db)
    prompt = create_prompt()
    llm = create_llm()

    return retriever, prompt, llm


# ============================================================
# CHAT LOOP | User Interaction
# ============================================================


def start_chat(retriever, prompt, llm):

    print("\n--- PDF Chatbot Initialized ---")
    print("Type 'exit' or 'quit' to stop.")

    while True:

        question = input("\n=====> You : ")

        if question.lower() in ["exit", "quit"]:
            print("Exiting...")
            break

        answer = ask_question(question, retriever, prompt, llm)

        print(f"\n=====> Agent : {answer}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    retriever, prompt, llm = create_rag_system()
    start_chat(retriever, prompt, llm)
