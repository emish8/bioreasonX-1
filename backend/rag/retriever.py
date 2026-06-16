import json
import os
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any

from backend.utils.config import LITERATURE_DB_PATH, FAISS_INDEX_DIR, logger
from backend.rag.embedder import BiomedicalEmbedder, HAS_FAISS

class BiomedicalRetriever:
    def __init__(self, embedder: BiomedicalEmbedder = None):
        self.embedder = embedder or BiomedicalEmbedder()
        self.documents: List[Dict[str, Any]] = []
        self.vectors: np.ndarray = None
        self.index = None
        self.doc_store_path = FAISS_INDEX_DIR / "documents.pkl"
        self.index_file_path = FAISS_INDEX_DIR / "faiss.index"
        
        self.initialize_index()

    def initialize_index(self, force_rebuild: bool = False):
        """Loads or builds the vector database index."""
        # 1. Load literature DB
        if not LITERATURE_DB_PATH.exists():
            logger.error(f"Literature database file not found at {LITERATURE_DB_PATH}!")
            return
            
        with open(LITERATURE_DB_PATH, "r", encoding="utf-8") as f:
            self.documents = json.load(f)
            
        logger.info(f"Loaded {len(self.documents)} source documents from {LITERATURE_DB_PATH}")

        # 2. Check if cached index exists
        if not force_rebuild and self.doc_store_path.exists() and (self.index_file_path.exists() or not HAS_FAISS):
            try:
                logger.info("Loading cached FAISS/Vector index...")
                with open(self.doc_store_path, "rb") as f:
                    cached_data = pickle.load(f)
                    self.documents = cached_data["documents"]
                    self.vectors = cached_data["vectors"]
                    
                if HAS_FAISS and self.index_file_path.exists():
                    import faiss
                    self.index = faiss.read_index(str(self.index_file_path))
                    logger.info("Successfully loaded FAISS index.")
                else:
                    logger.info("Loaded in-memory vectors for cosine similarity fallback search.")
                return
            except Exception as e:
                logger.warning(f"Error loading cached index: {e}. Rebuilding index...")

        # 3. Build index
        logger.info("Building new vector database index...")
        self.vectors, self.documents = self.embedder.embed_documents(self.documents)
        
        # Save cache
        with open(self.doc_store_path, "wb") as f:
            pickle.dump({"documents": self.documents, "vectors": self.vectors}, f)

        if HAS_FAISS:
            try:
                import faiss
                dimension = self.vectors.shape[1]
                # Normalize vectors for cosine similarity (Inner Product on normalized vectors is Cosine)
                norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
                # Avoid divide by zero
                norms = np.where(norms == 0, 1.0, norms)
                normalized_vectors = self.vectors / norms
                
                self.index = faiss.IndexFlatIP(dimension)
                self.index.add(normalized_vectors.astype('float32'))
                faiss.write_index(self.index, str(self.index_file_path))
                logger.info(f"FAISS index built and saved with {self.index.ntotal} entries.")
            except Exception as e:
                logger.error(f"Failed to build FAISS index: {e}. Falling back to in-memory cosine similarity.")
        else:
            logger.info("In-memory vector cache created for similarity searches.")

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieves top_k relevant documents for the query."""
        if not self.documents or self.vectors is None:
            logger.warning("Retriever index not initialized. Empty results returned.")
            return []

        logger.info(f"Executing RAG retrieval for: '{query}'")
        query_vector = self.embedder.embed_queries([query])

        if HAS_FAISS and self.index is not None:
            try:
                # Normalize query vector for cosine similarity
                norm = np.linalg.norm(query_vector, axis=1, keepdims=True)
                norm = np.where(norm == 0, 1.0, norm)
                normalized_query = query_vector / norm
                
                scores, indices = self.index.search(normalized_query.astype('float32'), top_k)
                
                results = []
                for score, idx in zip(scores[0], indices[0]):
                    if idx < 0 or idx >= len(self.documents):
                        continue
                    doc = self.documents[idx].copy()
                    # Convert cosine similarity score from inner product
                    doc["relevance_score"] = float(score)
                    results.append(doc)
                return results
            except Exception as e:
                logger.error(f"FAISS search failed: {e}. Falling back to numpy similarity search.")

        # Fallback numpy cosine similarity
        try:
            # Query vector norm
            q_norm = np.linalg.norm(query_vector, axis=1, keepdims=True)
            q_norm = np.where(q_norm == 0, 1.0, q_norm)
            q_normalized = query_vector / q_norm

            # Document vectors norm
            d_norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
            d_norms = np.where(d_norms == 0, 1.0, d_norms)
            d_normalized = self.vectors / d_norms

            # Cosine similarities
            scores = np.dot(d_normalized, q_normalized.T).flatten()
            
            # Sort top indices
            top_indices = np.argsort(scores)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                doc = self.documents[idx].copy()
                doc["relevance_score"] = float(scores[idx])
                results.append(doc)
            return results
        except Exception as e:
            logger.error(f"Numpy similarity calculation failed: {e}")
            # Dumb fallback: return top_k slice of database
            return [dict(doc, relevance_score=0.5) for doc in self.documents[:top_k]]
