from sentence_transformers import SentenceTransformer

class Embedder:
    _model = None

    @classmethod
    def get_model(cls):
        """
        Lazy-loads and caches the sentence-transformers model.
        """
        if cls._model is None:
            print("Loading sentence-transformers model: all-MiniLM-L6-v2...")
            # Automatically downloads to app cache folder specified in config.py
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Sentence-transformers model loaded successfully.")
        return cls._model

    @classmethod
    def embed_text(cls, text_list):
        """
        text_list: list of strings or single string
        Returns a list of list of floats (embeddings) or single list of floats
        """
        model = cls.get_model()
        # Convert single string input to list
        is_single = isinstance(text_list, str)
        if is_single:
            text_list = [text_list]
            
        embeddings = model.encode(text_list, show_progress_bar=False)
        
        # Convert numpy array to list for JSON/SQLite compatibility
        embeddings_list = embeddings.tolist()
        
        return embeddings_list[0] if is_single else embeddings_list
