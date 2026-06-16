import os
import json
import numpy as np
from typing import List, Dict, Any, Tuple
from backend.utils.config import logger

# Try importing sentence-transformers, fail gracefully to TF-IDF if necessary
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    logger.warning("sentence-transformers not installed or failed to import. Falling back to TF-IDF.")
    HAS_SENTENCE_TRANSFORMERS = False

# Try importing FAISS, fail gracefully to an in-memory cosine-similarity matrix
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    logger.warning("faiss-cpu not installed or failed to import. Falling back to in-memory cosine search.")
    HAS_FAISS = False

class BiomedicalEmbedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.vectorizer = None
        
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                logger.info(f"Loading HuggingFace Embedding Model: {model_name}")
                self.model = SentenceTransformer(model_name)
                # Quick dimensions check
                self.dimension = self.model.get_sentence_embedding_dimension()
                logger.info(f"HuggingFace Model loaded. Embedding dimensions: {self.dimension}")
            except Exception as e:
                logger.error(f"Error loading SentenceTransformer: {e}. Falling back to TF-IDF vectorizer.")
                self.setup_tfidf_fallback()
        else:
            self.setup_tfidf_fallback()

    def setup_tfidf_fallback(self):
        from sklearn.feature_extraction.text import TfidfVectorizer
        logger.info("Setting up TF-IDF Vectorizer fallback.")
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.dimension = None

    def embed_queries(self, texts: List[str]) -> np.ndarray:
        """Computes embeddings for queries. Returns a numpy array of shape (n_queries, dim)."""
        if self.model:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.astype('float32')
        else:
            # TF-IDF fallback
            if not hasattr(self.vectorizer, 'vocabulary_'):
                # Fit on texts to prevent crash (though fitting on query is bad, it acts as dummy fallback)
                self.vectorizer.fit(texts)
            matrix = self.vectorizer.transform(texts).toarray()
            return matrix.astype('float32')

    def embed_documents(self, documents: List[Dict[str, Any]]) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """Fits/computes embeddings for documents. Returns vectors and the original documents list."""
        texts = [f"Title: {doc['title']}\nAbstract: {doc['abstract']}" for doc in documents]
        
        if self.model:
            embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
            return embeddings.astype('float32'), documents
        else:
            # TF-IDF fallback
            logger.info("Fitting TF-IDF on document corpus.")
            matrix = self.vectorizer.fit_transform(texts).toarray()
            self.dimension = matrix.shape[1]
            return matrix.astype('float32'), documents
