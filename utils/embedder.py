import os
import requests
import json

class Embedder:
    _model = None

    @classmethod
    def get_model(cls):
        """
        Lazy-loads the local sentence-transformers model if available.
        Otherwise falls back to Hugging Face Inference API.
        """
        if cls._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                print("Loading local sentence-transformers model...")
                cls._model = SentenceTransformer('all-MiniLM-L6-v2')
                print("Sentence-transformers loaded locally.")
            except ImportError:
                print("sentence-transformers not installed. Will use Hugging Face Inference API.")
                cls._model = "api"
        return cls._model

    @classmethod
    def embed_text(cls, text_list):
        """
        text_list: list of strings or single string
        Returns embeddings using local sentence-transformers if present,
        otherwise queries Hugging Face Inference API.
        """
        model = cls.get_model()
        is_single = isinstance(text_list, str)
        inputs = [text_list] if is_single else text_list

        if model != "api":
            try:
                embeddings = model.encode(inputs, show_progress_bar=False)
                embeddings_list = embeddings.tolist()
                return embeddings_list[0] if is_single else embeddings_list
            except Exception as e:
                print(f"Local embed failed: {e}. Falling back to API.")

        # Hugging Face Inference API fallback
        url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
        headers = {"Content-Type": "application/json"}
        
        # Check if user has configured an API key or HF token in env
        hf_token = os.environ.get("HUGGINGFACE_API_KEY")
        if hf_token:
            headers["Authorization"] = f"Bearer {hf_token}"
            
        try:
            res = requests.post(url, headers=headers, json={"inputs": inputs}, timeout=25)
            if res.status_code == 200:
                out = res.json()
                if isinstance(out, list):
                    return out[0] if is_single else out
            print(f"HF API returned status {res.status_code}: {res.text}")
        except Exception as e:
            print(f"Error calling HF Inference API: {e}")

        # Final absolute fallback mock vectors if API is unreachable
        mock_dim = 384
        import random
        mock_vec = [random.uniform(-0.1, 0.1) for _ in range(mock_dim)]
        return mock_vec if is_single else [mock_vec for _ in inputs]
