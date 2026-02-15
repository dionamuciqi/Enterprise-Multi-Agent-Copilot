from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from retrieval.loader import load_documents, chunk_documents

PERSIST_DIR = ".chroma"


def index_documents(data_dir: str = "data"):
    embeddings = OpenAIEmbeddings()

    docs = load_documents(data_dir)
    chunks = chunk_documents(docs)

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR,
    )

    # In langchain-chroma, persistence is automatic when persist_directory is used.
    return vectordb


def get_vectorstore(data_dir: str = "data"):
    # If the persisted DB doesn't exist yet, create it
    if not Path(PERSIST_DIR).exists():
        return index_documents(data_dir)

    embeddings = OpenAIEmbeddings()
    return Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embeddings,
    )


def retrieve(query: str, k: int = 5, data_dir: str = "data"):
    vectordb = get_vectorstore(data_dir=data_dir)
    results = vectordb.similarity_search_with_score(query, k=min(30, max(10, k * 5)))

    seen = set()
    formatted = []

    for doc, score in results:
        key = (
            doc.metadata.get("source"),
            doc.metadata.get("page"),
            doc.metadata.get("chunk_id"),
        )
        if key in seen:
            continue
        seen.add(key)

        formatted.append({
            "text": doc.page_content,
            "source": doc.metadata.get("source"),
            "page": doc.metadata.get("page"),
            "chunk_id": doc.metadata.get("chunk_id"),
            "score": float(score),
        })

        if len(formatted) >= k:
            break

    return formatted

