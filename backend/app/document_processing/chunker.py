from langchain_text_splitters import RecursiveCharacterTextSplitter
from flask import current_app


def chunk_text(text, chunk_size=None, chunk_overlap=None):
    if chunk_size is None:
        chunk_size = current_app.config.get('RAG_CHUNK_SIZE', 1000)
    if chunk_overlap is None:
        chunk_overlap = current_app.config.get('RAG_CHUNK_OVERLAP', 200)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=['\n\n', '\n', '. ', ' ', ''],
    )
    return splitter.split_text(text)
