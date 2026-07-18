import os
import json
import numpy as np
from config import Config

class VectorStore:
    @staticmethod
    def get_index_path(user_id):
        """Returns the path to the user's vector storage file."""
        return os.path.join(Config.UPLOAD_FOLDER, f"vectors_user_{user_id}.json")

    @classmethod
    def load_index(cls, user_id):
        """Loads the user's index from disk. Returns a list of chunks with vectors."""
        path = cls.get_index_path(user_id)
        if not os.path.exists(path):
            return []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading vector index: {e}")
            return []

    @classmethod
    def save_index(cls, user_id, index_data):
        """Saves the user's index to disk."""
        path = cls.get_index_path(user_id)
        # Ensure parent folder exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f)
            return True
        except Exception as e:
            print(f"Error saving vector index: {e}")
            return False

    @classmethod
    def add_document(cls, user_id, doc_id, chunks, embeddings):
        """
        chunks: list of tuples (chunk_index, page_number, content)
        embeddings: list of list of floats
        """
        index_data = cls.load_index(user_id)
        
        # Format and append new records
        for i, chunk in enumerate(chunks):
            chunk_idx, page_num, content = chunk
            vector = embeddings[i]
            index_data.append({
                "doc_id": doc_id,
                "chunk_index": chunk_idx,
                "page_number": page_num,
                "content": content,
                "vector": vector
            })
            
        return cls.save_index(user_id, index_data)

    @classmethod
    def delete_document_index(cls, user_id, doc_id):
        """Removes all vectors belonging to a specific document from the user's index."""
        index_data = cls.load_index(user_id)
        filtered_index = [item for item in index_data if item["doc_id"] != doc_id]
        return cls.save_index(user_id, filtered_index)

    @classmethod
    def similarity_search(cls, user_id, query_vector, doc_id=None, top_k=4):
        """
        Performs vector similarity search using numpy-optimized cosine calculations.
        query_vector: list of floats
        doc_id: optional filter to limit search to a single document
        """
        index_data = cls.load_index(user_id)
        if not index_data:
            return []
            
        # Apply document filter if requested
        if doc_id is not None:
            index_data = [item for item in index_data if item["doc_id"] == doc_id]
            
        if not index_data:
            return []
            
        # Convert vectors to numpy array
        vectors = np.array([item["vector"] for item in index_data], dtype=np.float32)
        q_vec = np.array(query_vector, dtype=np.float32)
        
        # Calculate dot products
        dot_products = np.dot(vectors, q_vec)
        
        # Calculate norms
        vectors_norms = np.linalg.norm(vectors, axis=1)
        q_norm = np.linalg.norm(q_vec)
        
        # Guard against zero norms
        if q_norm == 0:
            return []
            
        # Cosine Similarity = dot_product / (norm(a) * norm(b))
        similarities = dot_products / (vectors_norms * q_norm + 1e-8)
        
        # Sort indices by similarity score descending
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            item = index_data[idx]
            results.append({
                "doc_id": item["doc_id"],
                "chunk_index": item["chunk_index"],
                "page_number": item["page_number"],
                "content": item["content"],
                "score": score
            })
            
        return results
