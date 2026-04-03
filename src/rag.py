import os
import requests
from typing import List
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

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
            "https://s2.q4cdn.com/299287126/files/doc_financials/2025/q2/AMZN-Q2-2025-Earnings-Release.pdf"
        ]
        
        for url in urls:
            filename = url.split("/")[-1]
            filepath = os.path.join(self.pdf_dir, filename)
            
            if not os.path.exists(filepath):
                print(f"Downloading {filename}...")
                response = requests.get(url)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded {filename}")
    
    def load_and_split_pdfs(self) -> List[Document]:
        documents = []
        
        for filename in os.listdir(self.pdf_dir):
            if filename.endswith('.pdf'):
                filepath = os.path.join(self.pdf_dir, filename)
                print(f"Processing {filename}...")
                
                reader = PdfReader(filepath)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                
                doc = Document(
                    page_content=text,
                    metadata={"source": filename}
                )
                documents.append(doc)
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        split_docs = text_splitter.split_documents(documents)
        print(f"Created {len(split_docs)} document chunks")
        
        return split_docs
    
    def create_vectorstore(self, documents: List[Document]):
        print("Creating vector store...")
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        self.vectorstore.save_local(self.index_dir)
        print("Vector store created and saved")
    
    def load_vectorstore(self):
        if os.path.exists(self.index_dir):
            print("Loading existing vector store...")
            self.vectorstore = FAISS.load_local(
                self.index_dir, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            print("Vector store loaded")
            return True
        return False
    
    def setup(self):
        if not self.load_vectorstore():
            self.download_pdfs()
            documents = self.load_and_split_pdfs()
            self.create_vectorstore(documents)
    
    def search(self, query: str, k: int = 4) -> List[Document]:
        if self.vectorstore is None:
            self.load_vectorstore()
        
        if self.vectorstore is None:
            raise ValueError("Vectorstore not initialized. Run setup() first.")
        
        return self.vectorstore.similarity_search(query, k=k)
