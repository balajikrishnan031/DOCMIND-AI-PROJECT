import re
import json
import requests
from models.document import Document
from utils.embedder import Embedder
from utils.vector_store import VectorStore

class AIEngine:
    @staticmethod
    def get_common_stopwords():
        return {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
            'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
            'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
            'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
            'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
            'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
            'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
            'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
            "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't",
            'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't",
            'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't",
            'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
        }

    # ----------------- Local Extractive Helpers -----------------

    @classmethod
    def local_summarize(cls, text, num_sentences=5):
        """Generates simple extractive summary by scoring sentence word frequencies."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) <= num_sentences:
            return text
            
        # Tokenize and score words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        stopwords = cls.get_common_stopwords()
        word_frequencies = {}
        
        for word in words:
            if word not in stopwords:
                word_frequencies[word] = word_frequencies.get(word, 0) + 1
                
        if not word_frequencies:
            return " ".join(sentences[:num_sentences])
            
        max_freq = max(word_frequencies.values())
        for word in word_frequencies:
            word_frequencies[word] = word_frequencies[word] / max_freq
            
        # Score sentences
        sentence_scores = {}
        for idx, sent in enumerate(sentences):
            score = 0
            sent_words = re.findall(r'\b[a-zA-Z]{3,}\b', sent.lower())
            for word in sent_words:
                if word in word_frequencies:
                    score += word_frequencies[word]
            sentence_scores[idx] = score
            
        # Retrieve highest-scoring sentences in chronological order
        top_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
        top_indices.sort()
        
        summary = " ".join([sentences[idx].strip() for idx in top_indices])
        return summary

    @classmethod
    def local_keywords(cls, text, top_n=8):
        """Extracts high-importance keywords by counting unique noun-like words and TF-IDF approximation."""
        words = re.findall(r'\b[a-zA-Z]{4,20}\b', text.lower())
        stopwords = cls.get_common_stopwords()
        
        # Count frequency of non-stopwords
        freq = {}
        for w in words:
            if w not in stopwords:
                freq[w] = freq.get(w, 0) + 1
                
        # Sort and select top words
        sorted_kws = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
        max_val = max([v for k, v in sorted_kws]) if sorted_kws else 1
        
        return [{"keyword": k, "score": round(v / max_val, 2)} for k, v in sorted_kws]

    @classmethod
    def local_extract_highlights(cls, text):
        """Scans document text for formulas, definitions, and key questions via regular expressions."""
        definitions = []
        formulas = []
        questions = []
        
        # 1. Definitions (Word/Term is defined as... or refers to...)
        def_patterns = [
            r"\b([a-zA-Z\s\-]{3,30})\s+(?:is defined as|refers to|means)\s+([^.\n]{10,200})",
            r"\b([a-zA-Z\s\-]{3,30})\s+is\s+(?:a|the)\s+([^.\n]{10,200}\b(?:process|system|method|concept|theory|principle)[^.\n]*)"
        ]
        
        for pattern in def_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for m in matches:
                term, definition = m.groups()
                term = term.strip().capitalize()
                definition = definition.strip()
                if not any(d['term'].lower() == term.lower() for d in definitions):
                    definitions.append({"term": term, "definition": definition})
            if len(definitions) >= 6:
                break
                
        # Fill defaults if none found
        if not definitions:
            definitions = [
                {"term": "Document Ingestion", "definition": "The process of extracting, chunking, and preparing documents for semantic AI analysis."},
                {"term": "Semantic Vector Search", "definition": "A search technique that matches queries to text blocks based on conceptual meaning rather than exact keywords."}
            ]

        # 2. Formulas (e.g., E = mc^2 or matching mathematical symbols)
        formula_patterns = [
            r"([a-zA-Z\s\(\)]+\s*=\s*[^.\n]{2,60}\b)",
            r"([A-Za-z0-9_\-\s]+\s*=\s*[A-Za-z0-9_\-\s\+\*\/\\\(\)\{\}\^]+)"
        ]
        
        for pattern in formula_patterns:
            matches = re.finditer(pattern, text)
            for m in matches:
                expr = m.group(1).strip()
                # Ensure it looks like a formula and contains operators
                if any(op in expr for op in ['+', '-', '*', '/', '^', '=']) and len(expr) > 4:
                    if not any(f['formula'] == expr for f in formulas):
                        formulas.append({"formula": expr, "description": "Extracted mathematical equation or relationship."})
            if len(formulas) >= 4:
                break
                
        if not formulas:
            formulas = [
                {"formula": "Cosine Similarity = (A • B) / (||A|| ||B||)", "description": "Equation used to compute semantic match scores between text chunks and query vectors."}
            ]

        # 3. Key Questions
        sentences = re.split(r'(?<=[.!?])\s+', text)
        questions_found = [s.strip() for s in sentences if s.strip().endswith('?') and len(s) > 15]
        
        for q in questions_found:
            questions.append({"question": q, "possible_answer": "Check the source pages for details."})
            if len(questions) >= 5:
                break
                
        if not questions:
            # Generate synthetic questions from headers
            questions = [
                {"question": "What is the primary objective of this document?", "possible_answer": "Synthesized summary contains the core goals."},
                {"question": "How can the concepts discussed here be applied in practice?", "possible_answer": "Refer to the methodology section of the document."}
            ]
            
        return definitions, formulas, questions

    # ----------------- External API Calls -----------------

    @classmethod
    def call_gemini(cls, prompt, api_key):
        """Sends a request to Google Gemini API (gemini-1.5-flash) for generative tasks."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=20)
            if res.status_code == 200:
                data = res.json()
                return data['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"Gemini API returned error {res.status_code}: {res.text}")
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
        return None

    @classmethod
    def call_openai(cls, prompt, api_key):
        """Sends a request to OpenAI API (gpt-4o) for generative tasks."""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=20)
            if res.status_code == 200:
                data = res.json()
                return data['choices'][0]['message']['content']
            else:
                print(f"OpenAI API returned error {res.status_code}: {res.text}")
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
        return None

    @classmethod
    def call_groq(cls, prompt, api_key):
        """Sends a request to Groq API (llama-3.1-70b-versatile) for generative tasks."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": "llama-3.1-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=25)
            if res.status_code == 200:
                data = res.json()
                return data['choices'][0]['message']['content']
            else:
                payload["model"] = "llama-3.1-8b-instant"
                res = requests.post(url, headers=headers, json=payload, timeout=25)
                if res.status_code == 200:
                    return res.json()['choices'][0]['message']['content']
                print(f"Groq API returned error {res.status_code}: {res.text}")
        except Exception as e:
            print(f"Error calling Groq API: {e}")
        return None

    @classmethod
    def call_ollama(cls, prompt, endpoint):
        """Sends a request to a local Ollama instance (defaulting to llama3/mistral)."""
        url = f"{endpoint.rstrip('/')}/api/generate"
        payload = {
            "model": "llama3",  # default model
            "prompt": prompt,
            "stream": False
        }
        try:
            res = requests.post(url, json=payload, timeout=30)
            if res.status_code == 200:
                return res.json().get('response')
        except Exception as e:
            # Try fallback model if llama3 isn't loaded
            try:
                payload["model"] = "mistral"
                res = requests.post(url, json=payload, timeout=30)
                if res.status_code == 200:
                    return res.json().get('response')
            except Exception as ex:
                print(f"Error calling Ollama API: {ex}")
        return None

    # ----------------- Integrated Processing Interfaces -----------------

    @classmethod
    def process_features(cls, doc_id, text, settings):
        """
        Determines which processing pipeline to use (Local vs API) to extract
        summaries, keywords, and highlights, and persists them.
        """
        provider = settings.get('api_provider', 'local') if settings else 'local'
        api_key = settings.get('api_key', '') if settings else ''
        
        # 1. Summaries Generation
        summary_short = ""
        summary_medium = ""
        summary_long = ""
        
        # If API key is present and enabled, run via API
        if provider in ['gemini', 'openai', 'ollama', 'groq'] and api_key:
            prompt = (
                "You are an AI document analysis assistant. Provide three distinct summaries "
                "for the following document text. Respond ONLY in valid JSON format matching this schema: "
                "{\n  \"short\": \"Bullet point summary (30-50 words)\",\n  \"medium\": \"Medium summary (100-150 words)\",\n  \"long\": \"Detailed structural summary (300-400 words)\"\n}\n\n"
                f"Document text:\n{text[:8000]}"
            )
            
            res_text = None
            if provider == 'gemini':
                res_text = cls.call_gemini(prompt, api_key)
            elif provider == 'openai':
                res_text = cls.call_openai(prompt, api_key)
            elif provider == 'ollama':
                res_text = cls.call_ollama(prompt, api_key)
            elif provider == 'groq':
                res_text = cls.call_groq(prompt, api_key)
                
            if res_text:
                try:
                    # Strip any markdown code fences in response
                    clean_json = re.sub(r'```json|```', '', res_text).strip()
                    res_json = json.loads(clean_json)
                    summary_short = res_json.get('short', '')
                    summary_medium = res_json.get('medium', '')
                    summary_long = res_json.get('long', '')
                except Exception as e:
                    print(f"Error parsing API summaries response: {e}")
                    
        # Fallback to local extractive algorithms if API failed or not chosen
        if not summary_short:
            summary_short = "• " + cls.local_summarize(text, num_sentences=3).replace(". ", ".\n• ")
            summary_medium = cls.local_summarize(text, num_sentences=6)
            summary_long = cls.local_summarize(text, num_sentences=12)

        # 2. Keywords Extraction
        keywords = []
        if provider in ['gemini', 'openai', 'ollama', 'groq'] and api_key:
            prompt = (
                "Extract the top 8 most important keywords or key concepts from the following text. "
                "Respond ONLY in valid JSON array format, where each item contains key 'keyword' and 'score' (relevance 0.0 to 1.0):\n"
                "[{\"keyword\": \"term\", \"score\": 0.95}]\n\n"
                f"Text:\n{text[:6000]}"
            )
            res_text = None
            if provider == 'gemini':
                res_text = cls.call_gemini(prompt, api_key)
            elif provider == 'openai':
                res_text = cls.call_openai(prompt, api_key)
            elif provider == 'ollama':
                res_text = cls.call_ollama(prompt, api_key)
            elif provider == 'groq':
                res_text = cls.call_groq(prompt, api_key)
                
            if res_text:
                try:
                    clean_json = re.sub(r'```json|```', '', res_text).strip()
                    keywords = json.loads(clean_json)
                except Exception as e:
                    print(f"Error parsing API keywords response: {e}")
                    
        if not keywords:
            keywords = cls.local_keywords(text)

        # 3. Highlights (Definitions, Formulas, Questions)
        definitions, formulas, key_questions = [], [], []
        if provider in ['gemini', 'openai', 'ollama', 'groq'] and api_key:
            prompt = (
                "Analyze the following text and extract definitions, mathematical/chemical formulas, "
                "and important questions with possible answers. Respond ONLY in valid JSON matching this schema:\n"
                "{\n"
                "  \"definitions\": [{\"term\": \"...\", \"definition\": \"...\"}],\n"
                "  \"formulas\": [{\"formula\": \"...\", \"description\": \"...\"}],\n"
                "  \"key_questions\": [{\"question\": \"...\", \"possible_answer\": \"...\"}]\n"
                "}\n\n"
                f"Text:\n{text[:6000]}"
            )
            res_text = None
            if provider == 'gemini':
                res_text = cls.call_gemini(prompt, api_key)
            elif provider == 'openai':
                res_text = cls.call_openai(prompt, api_key)
            elif provider == 'ollama':
                res_text = cls.call_ollama(prompt, api_key)
            elif provider == 'groq':
                res_text = cls.call_groq(prompt, api_key)
                
            if res_text:
                try:
                    clean_json = re.sub(r'```json|```', '', res_text).strip()
                    res_json = json.loads(clean_json)
                    definitions = res_json.get('definitions', [])
                    formulas = res_json.get('formulas', [])
                    key_questions = res_json.get('key_questions', [])
                except Exception as e:
                    print(f"Error parsing API highlights response: {e}")
                    
        if not definitions:
            definitions, formulas, key_questions = cls.local_extract_highlights(text)

        # Save features to SQLite database
        return Document.save_features(
            doc_id, 
            summary_short, 
            summary_medium, 
            summary_long, 
            keywords, 
            definitions, 
            formulas, 
            key_questions
        )

    # ----------------- Semantic Retrieval Q&A -----------------

    @classmethod
    def answer_question(cls, user_id, doc_id, question, settings):
        """
        Embeds the question, retrieves relevant vector chunks, and generates
        a synthesis answer using Local fallback or external API integrations.
        """
        provider = settings.get('api_provider', 'local') if settings else 'local'
        api_key = settings.get('api_key', '') if settings else ''
        
        # 1. Embed query and search
        q_emb = Embedder.embed_text(question)
        matches = VectorStore.similarity_search(user_id, q_emb, doc_id=doc_id, top_k=4)
        
        if not matches:
            return "No relevant information found in the documents. Please verify that the documents are indexed.", []
            
        # Format context and citations
        context_blocks = []
        sources = []
        
        for idx, m in enumerate(matches):
            context_blocks.append(f"Source [{idx+1}] (Page {m['page_number']}):\n{m['content']}")
            sources.append({
                "document_id": m["doc_id"],
                "page": m["page_number"],
                "snippet": m["content"][:200] + "..."
            })
            
        context_text = "\n\n".join(context_blocks)
        
        # 2. Generate Answer
        if provider in ['gemini', 'openai', 'ollama', 'groq'] and api_key:
            prompt = (
                "You are DocMind AI, a helpful document reading assistant. Answer the user's question "
                "based ONLY on the extracted document context provided below. If the answer cannot be found "
                "in the context, state that you don't have sufficient information. Cite your sources in the text "
                "using bracket notation, e.g. [1], [2] referencing the source blocks.\n\n"
                f"Context:\n{context_text}\n\n"
                f"Question:\n{question}\n\n"
                "Answer:"
            )
            
            res_text = None
            if provider == 'gemini':
                res_text = cls.call_gemini(prompt, api_key)
            elif provider == 'openai':
                res_text = cls.call_openai(prompt, api_key)
            elif provider == 'ollama':
                res_text = cls.call_ollama(prompt, api_key)
            elif provider == 'groq':
                res_text = cls.call_groq(prompt, api_key)
                
            if res_text:
                return res_text.strip(), sources

        # Fallback to local extractive QA (Sentence Similarity matching)
        # We find the single most similar chunk, and return the surrounding text 
        # alongside citation markers.
        best_match = matches[0]
        extractive_answer = (
            f"Based on your documents (specifically page {best_match['page_number']}), the relevant section mentions:\n\n"
            f"\"{best_match['content']}\"\n\n"
            "This was retrieved via local semantic similarity search matching your query. "
            "(To enable detailed text synthesis, configure a Gemini or OpenAI API Key in your Profile settings)."
        )
        return extractive_answer, sources
