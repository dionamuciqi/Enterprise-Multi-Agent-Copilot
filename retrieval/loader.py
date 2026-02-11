from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter



def load_documents(data_dir: str):
    docs = []
    for path in Path(data_dir).glob("*.pdf"):
        loaded = PyPDFLoader(str(path)).load()
        for d in loaded:
            d.metadata["source"] = path.name
        docs.extend(loaded)
    return docs


def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    chunks = splitter.split_documents(documents)
    for i, c in enumerate(chunks):
        c.metadata["chunk_id"] = f"chunk_{i}"
    return chunks
