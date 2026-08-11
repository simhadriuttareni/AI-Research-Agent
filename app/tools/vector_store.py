import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
import os
from app.utils.logger import logger

class VectorStore:
    """Vector database for storing and retrieving research data."""
    
    def __init__(self, collection_name: str = "research_docs"):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection_name = collection_name
        self.collection = self._get_or_create_collection()
        
    def _get_or_create_collection(self):
        """Get or create collection."""
        try:
            return self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_fn
            )
        except:
            return self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_fn
            )
    
    def add_documents(self, documents: List[Dict[str, Any]], metadata: Optional[List[Dict]] = None):
        """Add documents to vector store."""
        try:
            ids = [f"doc_{i}_{hash(doc.get('title', ''))}" for i, doc in enumerate(documents)]
            texts = [doc.get("content", "") for doc in documents]
            metadatas = metadata or [{"source": doc.get("url", ""), "title": doc.get("title", "")} for doc in documents]
            
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Vector store add error: {str(e)}")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            docs = []
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    docs.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0
                    })
            
            return docs
        except Exception as e:
            logger.error(f"Vector store search error: {str(e)}")
            return []