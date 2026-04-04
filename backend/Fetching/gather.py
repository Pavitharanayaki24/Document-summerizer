from langchain_community.document_loaders import PyPDFLoader # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter # type: ignore
from langchain_community.embeddings import HuggingFaceEmbeddings # type: ignore
from langchain_community.vectorstores import FAISS # type: ignore



def load_pdf(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents

def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    return chunks

def create_embeddings():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return embeddings

def store_in_vector_db(chunks, embeddings):
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local("vector_store")
    return vectorstore

def ingest_pipeline():
    
    file_path = r"P:\HR-policy bot\backend\fruitsandvegetable.pdf"

    print("Loading PDF")
    documents = load_pdf(file_path)

    print("Chunking documents")
    chunks = chunk_documents(documents)

    print("Creating embeddings")
    embeddings = create_embeddings()

    print("Storing in FAISS vector database")
    store_in_vector_db(chunks, embeddings)

    print("Ingestion completed successfully!")


if __name__ == "__main__":
    ingest_pipeline()