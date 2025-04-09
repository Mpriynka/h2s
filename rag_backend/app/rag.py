# app/rag.py
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import os

class RAGSystem:
    def __init__(self):
        # Initialize embeddings and LLM
        self.embeddings = OllamaEmbeddings(model="llama2")
        self.llm = Ollama(model="llama2")
        
        # Initialize vector store
        self.vector_store = None
        self.retriever = None
        self.qa_chain = None
        
        # Load existing vector store if available
        if os.path.exists("faiss_index"):
            self._load_vector_store()
    
    def _load_vector_store(self):
        """Safely load the FAISS vector store with proper deserialization settings"""
        try:
            self.vector_store = FAISS.load_local(
                "faiss_index",
                self.embeddings,
                allow_dangerous_deserialization=True  # Explicitly allow for trusted sources
            )
            self._setup_retriever()
        except Exception as e:
            print(f"Error loading vector store: {e}")
            # Create new empty vector store if loading fails
            self.vector_store = None
    
    def _setup_retriever(self):
        """Setup the retriever and QA chain"""
        if self.vector_store is None:
            return
            
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
        prompt_template = """Use the following pieces of context to answer the question at the end. 
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        {context}
        
        Question: {question}
        Answer:"""
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
    
    def ingest_pdf(self, file_path: str):
        """Process and ingest a PDF file"""
        try:
            # Load PDF
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            
            # Split text
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            texts = text_splitter.split_documents(pages)
            
            # Create or update vector store
            if self.vector_store is None:
                self.vector_store = FAISS.from_documents(texts, self.embeddings)
            else:
                self.vector_store.add_documents(texts)
            
            # Save the index
            self.vector_store.save_local("faiss_index")
            self._setup_retriever()
            
            return {"pages_processed": len(pages), "chunks_created": len(texts)}
        except Exception as e:
            print(f"Error ingesting PDF: {e}")
            raise
    
    def query(self, question: str, top_k: int = 3):
        """Query the knowledge base"""
        if self.qa_chain is None:
            return {"answer": "No knowledge base available", "source_documents": []}
        
        try:
            result = self.qa_chain({"query": question})
            return {
                "answer": result["result"],
                "source_documents": [doc.metadata for doc in result["source_documents"]]
            }
        except Exception as e:
            print(f"Error querying knowledge base: {e}")
            return {"answer": "Error processing your query", "source_documents": []}