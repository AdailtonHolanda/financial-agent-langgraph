import os
from typing import List

import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from pypdf import PdfReader


class AmazonReportRAG:
    def __init__(self, pdf_dir: str = "pdfs", index_dir: str = "faiss_index"):
        self.pdf_dir = pdf_dir
        self.index_dir = index_dir
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = None

        os.makedirs(pdf_dir, exist_ok=True)
        os.makedirs(index_dir, exist_ok=True)

    def download_pdfs(self):
        urls = [
            "https://s2.q4cdn.com/299287126/files/doc_financials/2025/q3/AMZN-Q3-2025-Earnings-Release.pdf",
            "https://s2.q4cdn.com/299287126/files/doc_financials/2025/q2/AMZN-Q2-2025-Earnings-Release.pdf",
        ]

        for url in urls:
            filename = url.split("/")[-1]
            filepath = os.path.join(self.pdf_dir, filename)

            if os.path.exists(filepath):
                continue

            print(f"Downloading {filename}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            with open(filepath, "wb") as file_obj:
                file_obj.write(response.content)
            print(f"Downloaded {filename}")

    def load_and_split_pdfs(self) -> List[Document]:
        documents = []

        for filename in os.listdir(self.pdf_dir):
            if not filename.lower().endswith(".pdf"):
                continue

            filepath = os.path.join(self.pdf_dir, filename)
            print(f"Processing {filename}...")

            reader = PdfReader(filepath)
            page_text = []
            for page in reader.pages:
                extracted = page.extract_text() or ""
                if extracted.strip():
                    page_text.append(extracted)

            text = "\n".join(page_text).strip()
            if not text:
                continue

            documents.append(
                Document(page_content=text, metadata={"source": filename})
            )

        if not documents:
            raise ValueError("No readable PDF documents were found for indexing.")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        split_docs = text_splitter.split_documents(documents)
        print(f"Created {len(split_docs)} document chunks")
        return split_docs

    def create_vectorstore(self, documents: List[Document]):
        if not documents:
            raise ValueError("Cannot create a vector store from an empty document list.")

        print("Creating vector store...")
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        self.vectorstore.save_local(self.index_dir)
        print("Vector store created and saved")

    def load_vectorstore(self):
        if not os.path.exists(self.index_dir):
            return False

        index_file = os.path.join(self.index_dir, "index.faiss")
        metadata_file = os.path.join(self.index_dir, "index.pkl")
        if not (os.path.exists(index_file) and os.path.exists(metadata_file)):
            return False

        print("Loading existing vector store...")
        self.vectorstore = FAISS.load_local(
            self.index_dir,
            self.embeddings,
            allow_dangerous_deserialization=True,
        )
        print("Vector store loaded")
        return True

    def setup(self):
        if self.load_vectorstore():
            return

        self.download_pdfs()
        documents = self.load_and_split_pdfs()
        self.create_vectorstore(documents)

    def search(self, query: str, k: int = 4) -> List[Document]:
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty.")

        if self.vectorstore is None and not self.load_vectorstore():
            raise ValueError("Vector store is not initialized. Run setup() first.")

        return self.vectorstore.similarity_search(query, k=k)
