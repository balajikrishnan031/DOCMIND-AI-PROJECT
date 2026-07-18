-- User Accounts
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Uploaded Documents
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_type TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'processing',
    target_grade TEXT DEFAULT 'College',
    target_role TEXT DEFAULT 'Student',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Text Chunks
CREATE TABLE IF NOT EXISTS document_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Document Features (Summaries, Keywords, Key Insights)
CREATE TABLE IF NOT EXISTS document_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER UNIQUE NOT NULL,
    summary_short TEXT,
    summary_medium TEXT,
    summary_long TEXT,
    keywords TEXT,        -- JSON array of keywords: ["ML", "Python", ...]
    definitions TEXT,     -- JSON array of {"term": "...", "definition": "..."}
    formulas TEXT,        -- JSON array of {"formula": "...", "description": "..."}
    key_questions TEXT,   -- JSON array of {"question": "...", "possible_answer": "..."}
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Q&A History
CREATE TABLE IF NOT EXISTS qa_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    document_id INTEGER,  -- NULL if searching all documents
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    sources TEXT,         -- JSON array of {"document_name": "...", "page": N, "snippet": "..."}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
);

-- User Settings
CREATE TABLE IF NOT EXISTS user_settings (
    user_id INTEGER UNIQUE PRIMARY KEY,
    api_provider TEXT DEFAULT 'local', -- 'local', 'openai', 'gemini', 'ollama'
    api_key TEXT,                       -- Encrypted or plain API Key
    theme TEXT DEFAULT 'dark',          -- 'dark' or 'light'
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Syllabus Units Table
CREATE TABLE IF NOT EXISTS syllabus_units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    unit_title TEXT NOT NULL,
    unit_index INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Syllabus Topics Table
CREATE TABLE IF NOT EXISTS syllabus_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id INTEGER NOT NULL,
    topic_name TEXT NOT NULL,
    document_id INTEGER,       -- Mapped book
    page_number INTEGER,       -- Mapped page
    status TEXT DEFAULT 'pending', -- 'pending' or 'covered'
    FOREIGN KEY (unit_id) REFERENCES syllabus_units(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
);

-- Flashcards Table
CREATE TABLE IF NOT EXISTS study_flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Quizzes Table
CREATE TABLE IF NOT EXISTS study_quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    options_json TEXT NOT NULL, -- JSON array of 4 options
    correct_option INTEGER NOT NULL, -- 0 to 3
    explanation TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Quiz Attempts Table
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    total INTEGER NOT NULL,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

