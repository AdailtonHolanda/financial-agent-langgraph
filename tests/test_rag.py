from pathlib import Path

import pytest

from src.rag import AmazonReportRAG


def build_rag_without_init(tmp_path: Path) -> AmazonReportRAG:
    rag = AmazonReportRAG.__new__(AmazonReportRAG)
    rag.pdf_dir = str(tmp_path / "pdfs")
    rag.index_dir = str(tmp_path / "faiss_index")
    rag.embeddings = None
    rag.vectorstore = None
    return rag


def test_search_rejects_empty_query(tmp_path):
    rag = build_rag_without_init(tmp_path)

    with pytest.raises(ValueError, match="Search query cannot be empty"):
        rag.search("   ")


def test_load_vectorstore_returns_false_when_index_files_are_missing(tmp_path):
    rag = build_rag_without_init(tmp_path)
    Path(rag.index_dir).mkdir(parents=True)

    assert rag.load_vectorstore() is False


def test_create_vectorstore_rejects_empty_documents(tmp_path):
    rag = build_rag_without_init(tmp_path)

    with pytest.raises(ValueError, match="empty document list"):
        rag.create_vectorstore([])
