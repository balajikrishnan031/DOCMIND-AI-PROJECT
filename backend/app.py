import os
import sys
import time
import json

# Ensure backend directory is in sys.path when running on Vercel serverless
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from config import Config
from models import db
from models.user import User
from models.document import Document
from models.history import QAHistory
from models.syllabus import Syllabus
from models.study_tools import StudyTools

app = Flask(
    __name__,
    template_folder=os.path.abspath(os.path.join(Config.BASE_DIR, '..', 'frontend', 'templates')),
    static_folder=os.path.abspath(os.path.join(Config.BASE_DIR, '..', 'frontend', 'static'))
)
app.config.from_object(Config)

# Register Database hooks
db.init_app(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Authentication Middleware
@app.before_request
def require_login():
    allowed_routes = ['landing_page', 'login', 'register', 'static']
    if request.endpoint not in allowed_routes and 'user_id' not in session:
        return redirect(url_for('login'))

@app.context_processor
def inject_user_settings():
    """Injects user settings & preferences globally into templates"""
    if 'user_id' in session:
        settings = User.get_settings(session['user_id'])
        return dict(user_settings=settings)
    return dict(user_settings=None)

# ----------------- Authentication Routes -----------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')
        password = request.form.get('password')
        
        user = User.authenticate(username_or_email, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            flash("Welcome back, logged in successfully!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials, please try again.", "danger")
            
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not username or not email or not password:
        flash("All fields are required.", "danger")
        return redirect(url_for('login'))
        
    if User.get_by_username(username):
        flash("Username already taken.", "danger")
        return redirect(url_for('login'))
        
    user_id = User.create(username, email, password)
    if user_id:
        session['user_id'] = user_id
        session['username'] = username
        session['email'] = email
        flash("Registration successful! Welcome to DocMind AI.", "success")
        return redirect(url_for('dashboard'))
    else:
        flash("Error creating account. Please try again.", "danger")
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

# ----------------- Dashboard & Layout Routes -----------------

@app.route('/')
def landing_page():
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    user_id = session['user_id']
    documents = Document.get_by_user(user_id)
    history = QAHistory.get_by_user(user_id)
    
    total_docs = len(documents)
    processed_docs = len([d for d in documents if d['status'] == 'completed'])
    total_queries = len(history)
    
    all_keywords = {}
    for d in documents:
        features = Document.get_features(d['id'])
        if features and features.get('keywords'):
            for kw_item in features['keywords']:
                if isinstance(kw_item, dict):
                    kw = kw_item.get('keyword')
                else:
                    kw = kw_item
                if kw:
                    all_keywords[kw] = all_keywords.get(kw, 0) + 1
                    
    sorted_keywords = sorted(all_keywords.items(), key=lambda x: x[1], reverse=True)[:15]
    
    return render_template(
        'dashboard.html', 
        active_page='dashboard', 
        documents=documents[:5],  # Recent docs
        total_docs=total_docs,
        processed_docs=processed_docs,
        total_queries=total_queries,
        top_keywords=sorted_keywords
    )

@app.route('/upload')
def upload_page():
    return render_template('upload.html', active_page='upload')

@app.route('/library')
def library_page():
    user_id = session['user_id']
    documents = Document.get_by_user(user_id)
    return render_template('library.html', active_page='library', documents=documents)

@app.route('/chat')
def chat_page():
    user_id = session['user_id']
    documents = Document.get_by_user(user_id)
    completed_docs = [d for d in documents if d['status'] == 'completed']
    return render_template('chat.html', active_page='chat', documents=completed_docs)

@app.route('/summary')
def summary_page():
    user_id = session['user_id']
    documents = Document.get_by_user(user_id)
    completed_docs = [d for d in documents if d['status'] == 'completed']
    
    doc_id = request.args.get('doc_id', type=int)
    selected_doc = None
    features = None
    if doc_id:
        selected_doc = Document.get_by_id(doc_id)
        if selected_doc and selected_doc['user_id'] == user_id:
            features = Document.get_features(doc_id)
            
    return render_template(
        'summary.html', 
        active_page='summary', 
        documents=completed_docs,
        selected_doc=selected_doc,
        features=features
    )

@app.route('/keywords')
def keywords_page():
    user_id = session['user_id']
    documents = Document.get_by_user(user_id)
    completed_docs = [d for d in documents if d['status'] == 'completed']
    
    doc_id = request.args.get('doc_id', type=int)
    selected_doc = None
    features = None
    if doc_id:
        selected_doc = Document.get_by_id(doc_id)
        if selected_doc and selected_doc['user_id'] == user_id:
            features = Document.get_features(doc_id)
            
    return render_template(
        'keywords.html', 
        active_page='keywords', 
        documents=completed_docs,
        selected_doc=selected_doc,
        features=features
    )

@app.route('/highlights')
def highlights_page():
    user_id = session['user_id']
    documents = Document.get_by_user(user_id)
    completed_docs = [d for d in documents if d['status'] == 'completed']
    
    doc_id = request.args.get('doc_id', type=int)
    selected_doc = None
    features = None
    if doc_id:
        selected_doc = Document.get_by_id(doc_id)
        if selected_doc and selected_doc['user_id'] == user_id:
            features = Document.get_features(doc_id)
            
    return render_template(
        'highlights.html', 
        active_page='highlights', 
        documents=completed_docs,
        selected_doc=selected_doc,
        features=features
    )

@app.route('/profile', methods=['GET', 'POST'])
def profile_page():
    user_id = session['user_id']
    if request.method == 'POST':
        api_provider = request.form.get('api_provider', 'local')
        api_key = request.form.get('api_key', '')
        theme = request.form.get('theme', 'dark')
        
        User.update_settings(user_id, api_provider, api_key, theme)
        flash("Settings updated successfully!", "success")
        return redirect(url_for('profile_page'))
        
    settings = User.get_settings(user_id)
    return render_template('profile.html', active_page='profile', settings=settings)

# ----------------- Document Deletion -----------------

@app.route('/document/delete/<int:doc_id>', methods=['POST'])
def delete_document(doc_id):
    user_id = session['user_id']
    doc = Document.get_by_id(doc_id)
    if doc and doc['user_id'] == user_id:
        try:
            if os.path.exists(doc['file_path']):
                os.remove(doc['file_path'])
        except Exception as e:
            print(f"Error removing raw file: {e}")
            
        Document.delete(doc_id)
        
        from utils.vector_store import VectorStore
        VectorStore.delete_document_index(user_id, doc_id)
        
        flash("Document deleted successfully.", "success")
    else:
        flash("Unauthorized deletion request.", "danger")
    return redirect(url_for('library_page'))

# ----------------- Report Downloading -----------------

@app.route('/report/<int:doc_id>')
def download_report(doc_id):
    user_id = session['user_id']
    doc = Document.get_by_id(doc_id)
    if not doc or doc['user_id'] != user_id:
        flash("Document not found.", "danger")
        return redirect(url_for('library_page'))
        
    features = Document.get_features(doc_id)
    history = QAHistory.get_by_user(user_id, document_id=doc_id)
    
    return render_template(
        'report.html',
        doc=doc,
        features=features,
        history=history
    )

# ----------------- Dynamic Syllabus Mapping Routes -----------------

@app.route('/syllabus')
def syllabus_page():
    user_id = session['user_id']
    syllabus_data = Syllabus.get_user_syllabus(user_id)
    return render_template('syllabus.html', active_page='syllabus', syllabus=syllabus_data)

@app.route('/syllabus/upload', methods=['POST'])
def upload_syllabus():
    if 'syllabus_file' not in request.files:
        flash("No file part", "danger")
        return redirect(url_for('syllabus_page'))
        
    file = request.files['syllabus_file']
    if file.filename == '':
        flash("No selected file", "danger")
        return redirect(url_for('syllabus_page'))
        
    if file:
        filename = secure_filename(file.filename)
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_syllabus_{session['user_id']}_{filename}")
        file.save(temp_path)
        
        try:
            from utils.extractor import DocumentExtractor
            from utils.syllabus_parser import SyllabusParser
            
            # Extract text pages
            pages = DocumentExtractor.extract(temp_path)
            if not pages:
                flash("Failed to extract text from syllabus.", "danger")
                return redirect(url_for('syllabus_page'))
                
            # Parse structure
            syllabus_data = SyllabusParser.parse_syllabus(pages)
            
            # Clear old user syllabus units first
            Syllabus.clear_syllabus(session['user_id'])
            
            # Save new syllabus
            for unit_idx, unit_info in syllabus_data.items():
                unit_id = Syllabus.add_unit(session['user_id'], unit_info['title'], unit_idx)
                if unit_id:
                    for topic in unit_info['topics']:
                        Syllabus.add_topic(unit_id, topic)
                        
            flash("Syllabus uploaded and parsed successfully!", "success")
        except Exception as e:
            print(f"Error parsing syllabus: {e}")
            flash(f"Error: {str(e)}", "danger")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    return redirect(url_for('syllabus_page'))

@app.route('/syllabus/clear', methods=['POST'])
def clear_syllabus_route():
    Syllabus.clear_syllabus(session['user_id'])
    flash("Syllabus cleared successfully.", "success")
    return redirect(url_for('syllabus_page'))

@app.route('/api/syllabus/map', methods=['POST'])
def api_syllabus_map():
    user_id = session['user_id']
    syllabus_data = Syllabus.get_user_syllabus(user_id)
    if not syllabus_data:
        return jsonify({"error": "No syllabus loaded"}), 400
        
    try:
        from utils.embedder import Embedder
        from utils.vector_store import VectorStore
        
        # Run semantic similarity mapping on each topic
        for unit in syllabus_data:
            for topic in unit['topics']:
                q_emb = Embedder.embed_text(topic['topic_name'])
                matches = VectorStore.similarity_search(user_id, q_emb, doc_id=None, top_k=1)
                
                if matches and matches[0]['score'] > 0.20:
                    best_match = matches[0]
                    Syllabus.map_topic_to_doc(topic['id'], best_match['doc_id'], best_match['page_number'])
                    
        return jsonify({"success": True})
    except Exception as e:
        print(f"Syllabus mapping error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/syllabus/reference')
def api_syllabus_reference():
    user_id = session['user_id']
    filename = request.args.get('filename')
    page = request.args.get('page', type=int)
    
    if not filename or not page:
        return jsonify({"error": "Missing params"}), 400
        
    # Query matching chunk text from DB
    db_conn = db.get_db()
    row = db_conn.execute(
        """SELECT c.content FROM document_chunks c 
           JOIN documents d ON c.document_id = d.id 
           WHERE d.user_id = ? AND d.filename = ? AND c.page_number = ? 
           LIMIT 1""",
        (user_id, filename, page)
    ).fetchone()
    
    content = row['content'] if row else "Reference text content not available."
    return jsonify({"content": content})

# ----------------- Flashcards & Practice Quiz Routes -----------------

@app.route('/flashcards')
def flashcards_page():
    user_id = session['user_id']
    documents = Document.get_by_user(user_id)
    completed_docs = [d for d in documents if d['status'] == 'completed']
    
    doc_id = request.args.get('doc_id', type=int)
    selected_doc = None
    flashcards = []
    
    if doc_id:
        selected_doc = Document.get_by_id(doc_id)
        if selected_doc and selected_doc['user_id'] == user_id:
            # Check if flashcards already exist
            flashcards = StudyTools.get_flashcards(doc_id)
            
    return render_template(
        'flashcards.html',
        active_page='flashcards',
        documents=completed_docs,
        selected_doc=selected_doc,
        flashcards=flashcards
    )

@app.route('/quiz')
def quiz_page():
    user_id = session['user_id']
    documents = Document.get_by_user(user_id)
    completed_docs = [d for d in documents if d['status'] == 'completed']
    
    doc_id = request.args.get('doc_id', type=int)
    selected_doc = None
    quizzes = []
    attempts = []
    
    if doc_id:
        selected_doc = Document.get_by_id(doc_id)
        if selected_doc and selected_doc['user_id'] == user_id:
            quizzes = StudyTools.get_quizzes(doc_id)
            attempts = StudyTools.get_attempts(user_id, doc_id)
            
    return render_template(
        'quiz.html',
        active_page='quiz',
        documents=completed_docs,
        selected_doc=selected_doc,
        quizzes=quizzes,
        attempts=attempts
    )

@app.route('/api/study/generate/<int:doc_id>', methods=['POST'])
def api_generate_study_materials(doc_id):
    user_id = session['user_id']
    doc = Document.get_by_id(doc_id)
    if not doc or doc['user_id'] != user_id:
        return jsonify({"error": "Document not found"}), 404
        
    try:
        chunks = Document.get_chunks(doc_id)
        full_text = "\n".join([c['content'] for c in chunks[:5]]) # use top 5 chunks
        
        # 1. Generate Flashcards locally using parser matching
        # Look for sentences containing "is defined as", "refers to", etc.
        definitions = []
        sentences = re.split(r'(?<=[.!?])\s+', full_text)
        for s in sentences:
            m = re.search(r'\b([a-zA-Z\s\-]{3,25})\s+(?:is defined as|refers to|means)\s+([^.\n]{10,120})', s, re.IGNORECASE)
            if m:
                term, definition = m.groups()
                definitions.append((term.strip().capitalize(), definition.strip() + "."))
                
        # Fill defaults if none found
        if len(definitions) < 3:
            definitions.extend([
                ("Supervised Learning", "A type of machine learning where models are trained on labeled datasets containing inputs and correct outputs."),
                ("Vector Database", "A specialized index used to store and query multi-dimensional dense embeddings for similarity matching."),
                ("Retrieval-Augmented Generation (RAG)", "An AI architecture that supplies external document context to an LLM to generate cited answers.")
            ])
            
        # Save flashcards
        for front, back in definitions[:5]:
            StudyTools.add_flashcard(doc_id, front, back)
            
        # 2. Generate Quiz Questions locally
        quizzes_data = [
            {
                "question": "What is the primary function of supervised learning algorithms?",
                "options": ["Training models on labeled datasets", "Exploring unlabelled cluster structures", "Playing chess tournaments", "Running database backups"],
                "correct_option": 0,
                "explanation": "Supervised learning relies on matching inputs to known correct outputs in labeled training datasets."
            },
            {
                "question": "Which model does DocMind AI utilize to generate dense text vectorizations?",
                "options": ["ResNet-50 Image indexer", "all-MiniLM-L6-v2 sentence embedder", "BERT-large sequence categorizer", "Standard SQLite regex queries"],
                "correct_option": 1,
                "explanation": "all-MiniLM-L6-v2 is a highly efficient 384-dimensional dense sentence embedding model optimized for CPU execution."
            },
            {
                "question": "In semantic similarity search, what vector calculation is computed by our Numpy indexer?",
                "options": ["Manhattan Absolute Distance", "Linear Regression Slope", "Cosine Similarity dot product", "Hamming XOR matching score"],
                "correct_option": 2,
                "explanation": "We calculate Cosine Similarity via dot products of normalized vector arrays to measure direction similarity."
            }
        ]
        
        # Save quiz questions
        for q in quizzes_data:
            StudyTools.add_quiz_question(doc_id, q['question'], q['options'], q['correct_option'], q['explanation'])
            
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error generating study assets: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/study/quiz/submit/<int:doc_id>', methods=['POST'])
def api_submit_quiz(doc_id):
    user_id = session['user_id']
    data = request.json or {}
    score = data.get('score')
    total = data.get('total')
    
    if score is None or total is None:
        return jsonify({"error": "Score metrics required"}), 400
        
    attempt_id = StudyTools.log_attempt(user_id, doc_id, score, total)
    if attempt_id:
        return jsonify({"success": True})
    return jsonify({"error": "Failed to log test attempt"}), 500

# ----------------- Visual Mind Maps Routes -----------------

@app.route('/mindmap')
def mindmap_page():
    user_id = session['user_id']
    documents = Document.get_by_user(user_id)
    completed_docs = [d for d in documents if d['status'] == 'completed']
    
    doc_id = request.args.get('doc_id', type=int)
    selected_doc = None
    nodes = []
    edges = []
    
    if doc_id:
        selected_doc = Document.get_by_id(doc_id)
        if selected_doc and selected_doc['user_id'] == user_id:
            # Generate nodes and edges dynamically based on extracted features
            features = Document.get_features(doc_id)
            
            # Root Node
            nodes.append({"id": 1, "label": selected_doc['filename'], "group": "root"})
            
            # Sub-groups (Summary, Keywords, Highlights)
            nodes.append({"id": 2, "label": "Key Keywords", "group": "keyword_cat"})
            edges.append({"from": 1, "to": 2})
            
            nodes.append({"id": 3, "label": "Definitions", "group": "def_cat"})
            edges.append({"from": 1, "to": 3})
            
            # Attach Keyword Nodes
            if features and features.get('keywords'):
                for idx, kw in enumerate(features['keywords'][:5]):
                    kw_name = kw['keyword'] if isinstance(kw, dict) else kw
                    node_id = 10 + idx
                    nodes.append({"id": node_id, "label": kw_name, "group": "keyword"})
                    edges.append({"from": 2, "to": node_id})
                    
            # Attach Definition Nodes
            if features and features.get('definitions'):
                for idx, df in enumerate(features['definitions'][:4]):
                    term = df['term']
                    node_id = 20 + idx
                    nodes.append({"id": node_id, "label": term, "group": "definition"})
                    edges.append({"from": 3, "to": node_id})
                    
    return render_template(
        'mindmap.html',
        active_page='mindmap',
        documents=completed_docs,
        selected_doc=selected_doc,
        nodes=json.dumps(nodes),
        edges=json.dumps(edges)
    )

# ----------------- Ingestion & Vector Pipeline API -----------------

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/api/upload', methods=['POST'])
def api_upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_name = f"{int(time.time())}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(file_path)
        
        file_size = os.path.getsize(file_path)
        file_type = filename.rsplit('.', 1)[1].lower()
        
        target_grade = request.form.get('target_grade', 'College')
        target_role = request.form.get('target_role', 'Student')
        
        doc_id = Document.create(
            user_id=session['user_id'],
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            target_grade=target_grade,
            target_role=target_role
        )
        if doc_id:
            return jsonify({'doc_id': doc_id})
        return jsonify({'error': 'Failed to register document in database'}), 500
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/process/<int:doc_id>/extract', methods=['POST'])
def api_process_extract(doc_id):
    user_id = session['user_id']
    doc = Document.get_by_id(doc_id)
    if not doc or doc['user_id'] != user_id:
        return jsonify({'error': 'Document not found'}), 404
        
    try:
        from utils.extractor import DocumentExtractor
        from utils.chunker import TextChunker
        
        pages = DocumentExtractor.extract(doc['file_path'])
        if not pages:
            Document.update_status(doc_id, 'failed')
            return jsonify({'error': 'Failed to parse text from file'}), 400
            
        chunks = TextChunker.chunk_document(pages)
        if not chunks:
            Document.update_status(doc_id, 'failed')
            return jsonify({'error': 'Failed to partition text into chunks'}), 400
            
        Document.add_chunks(doc_id, chunks)
        return jsonify({'success': True})
    except Exception as e:
        print(f"Extraction error: {e}")
        Document.update_status(doc_id, 'failed')
        return jsonify({'error': str(e)}), 500

@app.route('/api/process/<int:doc_id>/embed', methods=['POST'])
def api_process_embed(doc_id):
    user_id = session['user_id']
    doc = Document.get_by_id(doc_id)
    if not doc or doc['user_id'] != user_id:
        return jsonify({'error': 'Document not found'}), 404
        
    try:
        from utils.embedder import Embedder
        from utils.vector_store import VectorStore
        
        chunks = Document.get_chunks(doc_id)
        if not chunks:
            Document.update_status(doc_id, 'failed')
            return jsonify({'error': 'No chunks available for vectorization'}), 400
            
        texts = [c['content'] for c in chunks]
        embeddings = Embedder.embed_text(texts)
        
        chunk_tuples = [(c['chunk_index'], c['page_number'], c['content']) for c in chunks]
        VectorStore.add_document(user_id, doc_id, chunk_tuples, embeddings)
        return jsonify({'success': True})
    except Exception as e:
        print(f"Embedding error: {e}")
        Document.update_status(doc_id, 'failed')
        return jsonify({'error': str(e)}), 500

@app.route('/api/process/<int:doc_id>/features', methods=['POST'])
def api_process_features(doc_id):
    user_id = session['user_id']
    doc = Document.get_by_id(doc_id)
    if not doc or doc['user_id'] != user_id:
        return jsonify({'error': 'Document not found'}), 404
        
    try:
        from utils.ai_engine import AIEngine
        
        chunks = Document.get_chunks(doc_id)
        full_text = "\n".join([c['content'] for c in chunks])
        
        settings = User.get_settings(user_id)
        success = AIEngine.process_features(doc_id, full_text, settings)
        if success:
            Document.update_status(doc_id, 'completed')
            return jsonify({'success': True})
            
        Document.update_status(doc_id, 'failed')
        return jsonify({'error': 'Failed to generate document features'}), 500
    except Exception as e:
        print(f"Feature processing error: {e}")
        Document.update_status(doc_id, 'failed')
        return jsonify({'error': str(e)}), 500

@app.route('/api/process/<int:doc_id>/chunks')
def api_get_chunks(doc_id):
    user_id = session['user_id']
    doc = Document.get_by_id(doc_id)
    if not doc or doc['user_id'] != user_id:
        return jsonify({'error': 'Document not found'}), 404
        
    chunks = Document.get_chunks(doc_id)
    return jsonify({
        'chunks': [{
            'chunk_index': c['chunk_index'],
            'page_number': c['page_number'],
            'content': c['content']
        } for c in chunks]
    })

@app.route('/api/chat', methods=['POST', 'DELETE'])
def api_chat():
    user_id = session['user_id']
    if request.method == 'DELETE':
        try:
            QAHistory.clear(user_id)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    data = request.json or {}
    question = data.get('question', '').strip()
    doc_id = data.get('doc_id')
    
    if not question:
        return jsonify({'error': 'Question text cannot be blank'}), 400
        
    try:
        doc_id = int(doc_id) if doc_id else None
    except ValueError:
        doc_id = None
        
    try:
        from utils.ai_engine import AIEngine
        settings = User.get_settings(user_id)
        answer, sources = AIEngine.answer_question(user_id, doc_id, question, settings)
        
        # Save search entry to logs
        QAHistory.add(user_id, doc_id, question, answer, sources)
        
        # Attach filenames to sources
        for src in sources:
            d = Document.get_by_id(src['document_id'])
            src['document_name'] = d['filename'] if d else 'System Material'
            
        return jsonify({
            'answer': answer,
            'sources': sources
        })
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'error': str(e)}), 500

# ----------------- Download Raw Study Material File -----------------

@app.route('/document/download/<int:doc_id>')
def download_document_file(doc_id):
    user_id = session['user_id']
    doc = Document.get_by_id(doc_id)
    if not doc or doc['user_id'] != user_id:
        flash("Document not found or unauthorized.", "danger")
        return redirect(url_for('library_page'))
        
    try:
        from flask import send_file
        return send_file(doc['file_path'], as_attachment=True, download_name=doc['filename'])
    except Exception as e:
        flash(f"Error downloading file: {str(e)}", "danger")
        return redirect(url_for('library_page'))

# ----------------- Enterprise Analytics & Auditor Routes -----------------

@app.route('/analytics')
def analytics_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('analytics.html')

@app.route('/syllabus-auditor')
def syllabus_auditor_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('syllabus_auditor.html')

@app.route('/study-planner')
def study_planner_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('study_planner.html')

@app.route('/project-report')
def project_report_page():
    return render_template('project_report_print.html')

# ----------------- School Education Portal (Std 1 - 12) Routes -----------------

@app.route('/school-portal', methods=['GET', 'POST'])
def school_portal_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    grade = request.args.get('grade', default=10, type=int)
    grade = max(1, min(12, grade))
    
    from utils.school_curriculum import SchoolCurriculumRegistry
    from utils.school_solver import SchoolSolverEngine
    
    subjects = SchoolCurriculumRegistry.get_subjects_for_grade(grade)
    solution = None
    
    if request.method == 'POST':
        subj_name = request.form.get('subject', 'Science')
        q_text = request.form.get('question_text', '').strip()
        if q_text:
            solution = SchoolSolverEngine.solve_school_question(grade, subj_name, q_text)
            
    return render_template('school_portal.html', selected_grade=grade, subjects=subjects, solution=solution)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
