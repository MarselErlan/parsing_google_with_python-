import os
from dotenv import load_dotenv
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate

# Load API key from .env file
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Create LLM
llm = OpenAI(model_name="gpt-4o-mini", temperature=0.7)

# Function to build modern RAG chain
def create_modern_rag_chain(retriever, llm):
    rag_prompt = PromptTemplate.from_template("""
Use the following context to answer the question. If you don't know the answer, just say that you don't know.

Context: {context}
Question: {question}

Answer:
""")

    def ask_question(query_dict):
        question = query_dict["input"]
        docs = retriever.invoke(question)
        context = "\n\n".join([doc.page_content for doc in docs])
        answer = llm.invoke(rag_prompt.format(context=context, question=question))
        return {
            "answer": answer,
            "context": docs,
            "source_documents": docs
        }

    return ask_question

# Build and run the RAG chain
try:
    # Load PDF
    docs = PyPDFLoader("docs/Eric_Abram_1.pdf").load()  # Change to your actual file
    vector_store = FAISS.from_documents(docs, OpenAIEmbeddings())
    retriever = vector_store.as_retriever()

    rag_chain = create_modern_rag_chain(retriever, llm)

    # Ask a test question
    print("=== RAG Chain Example ===")
    response = rag_chain({"input": "What is this PDF about?"})
    print("Answer:", response["answer"])

except ImportError as e:
    print(f"Missing dependencies for RAG: {e}")
    print("Install with: pip install langchain-community PyPDF2 faiss-cpu")
