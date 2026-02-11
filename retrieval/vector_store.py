from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from retrieval.loader import load_documents, chunk_documents

PERSIST_DIR = ".chroma"


def index_documents(data_dir: str):
    embeddings = OpenAIEmbeddings()
    docs = load_documents(data_dir)
    chunks = chunk_documents(docs)

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR
    )
    vectordb.persist()
    return vectordb


def get_vectorstore():
    embeddings = OpenAIEmbeddings()
    return Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings
    )


def retrieve(query: str, k: int = 5):
    vectordb = get_vectorstore()
    results = vectordb.similarity_search_with_score(query, k=k)

    formatted = []
    for doc, score in results:
        formatted.append({
            "text": doc.page_content,
            "source": doc.metadata.get("source"),
            "page": doc.metadata.get("page"),
            "chunk_id": doc.metadata.get("chunk_id"),
            "score": float(score),
        })
    return formatted
