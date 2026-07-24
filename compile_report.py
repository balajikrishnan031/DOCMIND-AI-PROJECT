import os
import sys
import subprocess
import time
from PIL import Image, ImageDraw, ImageFont
import pypdf

print("=== STARTING INTERNSHIP REPORT COMPILER ===")

workspace_dir = "e:\\Docmind ai"
first_page_path = os.path.join(workspace_dir, "Balaji_Report_FirstPage Copy.pdf")
inplant_cert_path = os.path.join(workspace_dir, "cropped_IMG20260711205719.jpg")
project_cert_path = os.path.join(workspace_dir, "cropped_IMG20260711205702.jpg")
attendance_path = os.path.join(workspace_dir, "IMG_20260724_222927.jpg")
final_output_path = os.path.join(workspace_dir, "Balaji_Internship_Report.pdf")

# Temporary files paths
temp_inplant_pdf = os.path.join(workspace_dir, "temp_inplant.pdf")
temp_project_pdf = os.path.join(workspace_dir, "temp_project.pdf")
temp_attendance_pdf = os.path.join(workspace_dir, "temp_attendance.pdf")
temp_html_path = os.path.join(workspace_dir, "temp_report.html")
temp_chapters_pdf = os.path.join(workspace_dir, "temp_chapters.pdf")
edge_profile_dir = os.path.join(workspace_dir, "temp_edge_profile")

# Helper function to convert image to A4 PDF with proper scaling
def convert_img_to_a4_pdf(img_path, pdf_path):
    if not os.path.exists(img_path):
        print(f"[ERROR] Image not found: {img_path}")
        sys.exit(1)
    try:
        img = Image.open(img_path)
        a4_w, a4_h = 2480, 3508  # A4 size at 300 DPI
        
        # Calculate aspect ratio
        img_ratio = img.width / img.height
        a4_ratio = a4_w / a4_h
        
        if img_ratio > a4_ratio:
            new_w = a4_w
            new_h = int(a4_w / img_ratio)
        else:
            new_h = a4_h
            new_w = int(a4_h * img_ratio)
            
        resized_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Paste centered on a white canvas
        canvas = Image.new('RGB', (a4_w, a4_h), 'white')
        x_offset = (a4_w - new_w) // 2
        y_offset = (a4_h - new_h) // 2
        canvas.paste(resized_img, (x_offset, y_offset))
        canvas.save(pdf_path, 'PDF')
        print(f"[OK] Converted {os.path.basename(img_path)} to A4 PDF: {pdf_path}")
    except Exception as e:
        print(f"[ERROR] Image conversion failed for {img_path}: {e}")
        sys.exit(1)

# 1. Check first page PDF exists
if not os.path.exists(first_page_path):
    print(f"[ERROR] First page PDF not found at {first_page_path}")
    sys.exit(1)
print(f"[OK] Found first page PDF: {first_page_path}")

# 2. Convert JPEGs to PDFs
convert_img_to_a4_pdf(inplant_cert_path, temp_inplant_pdf)
convert_img_to_a4_pdf(project_cert_path, temp_project_pdf)
convert_img_to_a4_pdf(attendance_path, temp_attendance_pdf)

# 3. Generate the HTML template for Page 5 onwards (Acknowledgement, Abstract, Chapters 1-8)
html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DocMind AI - Academic Internship Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;1,400&family=Inter:wght@400;500;600;700&display=swap');
        
        body {
            background-color: #ffffff;
            color: #1a1715;
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }

        .container {
            width: 100%;
            max-width: 900px;
            margin: 0 auto;
            padding: 3rem;
        }

        .page {
            page-break-after: always;
            position: relative;
            min-height: 1100px;
            box-sizing: border-box;
            padding-bottom: 3.5rem;
        }
        .page:last-child {
            page-break-after: avoid !important;
            min-height: auto;
        }

        h1.section-title {
            font-family: 'Playfair Display', serif;
            font-size: 2.2rem;
            border-bottom: 2px solid #c97f5a;
            padding-bottom: 0.8rem;
            margin-top: 1rem;
            margin-bottom: 2rem;
            color: #1a1715;
        }
        h2.sub-section-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.4rem;
            margin-top: 1.8rem;
            margin-bottom: 0.8rem;
            color: #c97f5a;
        }
        h3.block-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.1rem;
            font-weight: 600;
            margin-top: 1.2rem;
            margin-bottom: 0.5rem;
            color: #1a1715;
        }
        p {
            margin-bottom: 1.2rem;
            color: #403a35;
            text-align: justify;
            font-size: 1rem;
        }
        ul, ol {
            margin-left: 2rem;
            margin-bottom: 1.2rem;
            color: #403a35;
            font-size: 1rem;
        }
        li {
            margin-bottom: 0.5rem;
        }
        
        pre {
            background-color: #2e2a24;
            color: #f7f4ee;
            padding: 1.25rem;
            border-radius: 8px;
            font-family: monospace;
            font-size: 0.85rem;
            overflow-x: auto;
            margin: 1.5rem 0;
        }

        .screenshot-container {
            margin: 2rem 0;
            border: 1px solid #e6dfd5;
            border-radius: 8px;
            overflow: hidden;
            background-color: #faf6f0;
            padding: 0.5rem;
            text-align: center;
        }
        .screenshot-img {
            width: 100%;
            height: auto;
            max-height: 380px;
            object-fit: contain;
            border-radius: 4px;
        }
        .screenshot-caption {
            font-size: 0.85rem;
            color: #6e655f;
            margin-top: 0.5rem;
            font-style: italic;
        }

        .tech-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            font-size: 0.95rem;
        }
        .tech-table th, .tech-table td {
            border: 1px solid #e6dfd5;
            padding: 0.8rem 1rem;
            text-align: left;
        }
        .tech-table th {
            background-color: #faf6f0;
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
        }

        .page-footer {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            display: flex;
            justify-content: space-between;
            font-size: 0.85rem;
            color: #8c827a;
            border-top: 1px solid #e6dfd5;
            padding-top: 0.5rem;
        }

        @media print {
            body {
                background-color: #ffffff !important;
                color: #000000 !important;
            }
            .page {
                min-height: 100% !important;
                page-break-after: always !important;
            }
        }
    </style>
</head>
<body>
    <div class="container">

        <!-- ================= PAGE 5: ACKNOWLEDGEMENT ================= -->
        <div class="page">
            <h1 class="section-title" style="text-align: center;">Acknowledgement</h1>
            <p>
                First and foremost, I would like to express my deep sense of gratitude and sincere thanks to the management of <strong>CodeBind Technologies, Chennai</strong>, for providing me with the wonderful opportunity to undergo my internship and in-plant training at their esteemed organization. I am highly obliged for the resources, facilities, and guidance made available to me during this period, which enabled a highly productive learning experience.
            </p>
            <p>
                I express my sincere and deep gratitude to <strong>Dr. S. SIVANESH</strong>, Head of the Department of Computer Science and Engineering, <strong>University College of Engineering, Panruti</strong>, for his valuable support, encouragement, and for providing the academic permission to carry out this internship training program. His leadership and guidance have been a constant source of inspiration throughout my academic journey.
            </p>
            <p>
                I am extremely grateful to my internship trainer and software engineering mentors at CodeBind Technologies, Chennai, for their expert guidance, constructive feedback, and invaluable mentoring throughout my training. Their practical insights into Python scripting, database administration, SQL querying, and vector similarity models have greatly enriched my technical skillset and analytical thinking.
            </p>
            <p>
                Lastly, I extend my heartfelt thanks to my parents and friends for their continuous support, patience, and motivation, which helped me focus on completing this industrial internship successfully.
            </p>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 5</span>
            </div>
        </div>

        <!-- ================= PAGE 6: ABSTRACT ================= -->
        <div class="page">
            <h1 class="section-title" style="text-align: center;">Abstract</h1>
            <p>
                During my intensive industrial internship and in-plant training at <strong>CodeBind Technologies, Chennai</strong>, in the specialized domain of <strong>Python with Artificial Intelligence & Machine Learning (AIML)</strong>, I acquired comprehensive hands-on exposure and practical training spanning the complete pipeline lifecycle of semantic document indexers and educational assistants.
            </p>
            <p>
                The curriculum of this training was designed to cover industry-standard tools, starting with foundational programming concepts in Python, moving to structured database administration with SQLite/SQL schemas, progressing to advanced vector semantic embedding structures using `Sentence-Transformers`, and concluding with interactive dashboard user interface visualizations using Vis.js and CSS 3D perspectives.
            </p>
            <p>
                To apply these skills, I built a final end-to-end project on <strong>'DocMind AI'</strong>. This involved extracting clean text pages from PDFs, chunking paragraphs with overlap bounds, generating 384-dimensional dense embeddings vector indexes, executing cosine similarity checks with NumPy matrix math, and building portals for syllabus auditing, active recall scoreboards, and Standard 1-12 curriculum solvers. This project experience strengthened my technical capabilities, providing me with the essential tools required to extract, index, and query unstructured documents into strategic, educational retrieval assets.
            </p>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 6</span>
            </div>
        </div>

        <!-- ================= PAGE 7: CHAPTER 1 ================= -->
        <div class="page">
            <h1 class="section-title">1. Introduction to Document Intelligence</h1>
            <p>
                In academic workflows, standard search mechanisms are constrained by literal string queries. If a student searches for "CPU Scheduling latency," a textbook section discussing "Round Robin wait times" will be missed entirely. This failure highlights the need for semantic document retrieval systems.
            </p>
            <p>
                <strong>DocMind AI</strong> is an intelligent document organizer and educational assistant that utilizes Retrieval-Augmented Generation (RAG) to index textbooks semantically. The application automatically maps unit topics to page references, creates study recall aids (quizzes, flashcards), and visualizes connection mind maps.
            </p>
            <div class="screenshot-container">
                <img src="file:///E:/Docmind%20ai/frontend/static/assets/docmind_ai_logo.png" alt="DocMind Logo" class="screenshot-img" style="max-height: 180px;">
                <div class="screenshot-caption">Figure 1.1: DocMind AI Project Brand Logo</div>
            </div>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 7</span>
            </div>
        </div>

        <!-- ================= PAGE 8 ================= -->
        <div class="page">
            <h1 class="section-title">1. Traditional vs Semantic Search</h1>
            <p>
                Keyword-based information retrieval systems match literal strings, ignoring context. Semantic information retrieval, however, matches concepts by mapping strings into high-dimensional vector spaces where distance represents similarity.
            </p>
            <p>
                By implementing this system, we bridge the gap between structured syllabus guidelines and unstructured textbook pages, saving time and improving active recall during exams.
            </p>
            <div class="screenshot-container">
                <img src="file:///E:/Docmind%20ai/frontend/static/assets/hero_screenshot.png" alt="DocMind Landing" class="screenshot-img">
                <div class="screenshot-caption">Figure 1.2: Redesigned Glassmorphic Landing Web Interface</div>
            </div>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 8</span>
            </div>
        </div>

        <!-- ================= PAGE 9 ================= -->
        <div class="page">
            <h1 class="section-title">2. Python for AI & Data Manipulation</h1>
            <p>
                Python is the primary language used to build DocMind AI due to its clear syntax and extensive scientific libraries. Essential programming structures implemented in our RAG pipeline include:
            </p>
            <h2 class="sub-section-title">2.1 Execution Paradigms</h2>
            <p>
                We use an interpreted environment for rapid preprocessing pipelines. Character-level tokenizers and coordinate boundary checkers parse textbook pages efficiently.
            </p>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 9</span>
            </div>
        </div>

        <!-- ================= PAGE 10 ================= -->
        <div class="page">
            <h1 class="section-title">2. Variables, Data Types & Formatting</h1>
            <p>
                Python's dynamic typing automatically detects primitive representations of text chunks and metrics:
            </p>
            <ul>
                <li><strong>Integer (int):</strong> Page counts, character lengths, and chunk sizes (e.g. `chunk_size = 1000`).</li>
                <li><strong>Float (float):</strong> Math vector values and similarity match scores (e.g. `similarity_threshold = 0.30`).</li>
                <li><strong>String (str):</strong> Paragraph text, filenames, and API prompts.</li>
                <li><strong>Boolean (bool):</strong> Processing and sync states (e.g. `is_indexed = True`).</li>
            </ul>
            <pre>
# Initializing typed fields in Python
document_id = 142
chunk_score = 0.8524
document_name = "os_textbook.pdf"
is_completed = True
            </pre>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 10</span>
            </div>
        </div>

        <!-- ================= PAGE 11 ================= -->
        <div class="page">
            <h1 class="section-title">2. Control Flow & Conditional Statements</h1>
            <p>
                Conditional execution routes raw text to different processing paths:
            </p>
            <pre>
# Route query based on matching score
if score >= similarity_threshold:
    context = matches[0]["content"]
    answer = call_llm(query, context)
else:
    answer = call_general_llm(query)
            </pre>
            <p>
                This routing enables the Q&A fallback mechanism when the query doesn't match the textbook context.
            </p>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 11</span>
            </div>
        </div>

        <!-- ================= PAGE 12 ================= -->
        <div class="page">
            <h1 class="section-title">2. Loop Iterations & Logic Skips</h1>
            <p>
                Loops iterate through document paragraphs, while control statements skip empty sections:
            </p>
            <pre>
# Process paragraphs, skipping empty strings
for p in paragraphs:
    if not p.strip():
        continue
    vectors.append(model.encode(p))
            </pre>
            <p>
                This ensures only valid text sections are processed.
            </p>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 12</span>
            </div>
        </div>

        <!-- ================= PAGE 13 ================= -->
        <div class="page">
            <h1 class="section-title">2. Functions & Advanced Lambda Expressions</h1>
            <p>
                User-defined functions process text chunks modularly, while inline lambda expressions sort vectors by match scores:
            </p>
            <pre>
# Sort search results by similarity score
results.sort(key=lambda x: x["score"], reverse=True)
            </pre>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 13</span>
            </div>
        </div>

        <!-- ================= PAGE 14 ================= -->
        <div class="page">
            <h1 class="section-title">2. Lists & Ordered Data Handling</h1>
            <p>
                Lists are mutable collections used to maintain chronological page records and ordered text paragraphs:
            </p>
            <pre>
# Initializing lists of text chunks
chunks = ["Paragraph 1", "Paragraph 2"]
chunks.append("Paragraph 3")
chunks.remove("Paragraph 1")
            </pre>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 14</span>
            </div>
        </div>

        <!-- ================= PAGE 15 ================= -->
        <div class="page">
            <h1 class="section-title">2. Dictionaries & Key-Value Configurations</h1>
            <p>
                Dictionaries map strings to complex structured values:
            </p>
            <pre>
# Metadata dict mapping
metadata = {
    "document_id": 1,
    "page_number": 3,
    "content": "Operating systems process scheduling policies...",
    "vector_dimensions": 384
}
            </pre>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 15</span>
            </div>
        </div>

        <!-- ================= PAGE 16 ================= -->
        <div class="page">
            <h1 class="section-title">2. Sets & Unique Term Filtering</h1>
            <p>
                Sets are unordered collections of unique elements, used to filter unique keywords:
            </p>
            <pre>
# Filter unique terms
words = ["cpu", "memory", "cpu", "disk"]
unique_keywords = set(words)  # {'cpu', 'memory', 'disk'}
            </pre>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 16</span>
            </div>
        </div>

        <!-- ================= PAGE 17 ================= -->
        <div class="page">
            <h1 class="section-title">3. Relational SQL Databases</h1>
            <p>
                DocMind AI uses a relational database schema to persist student credentials, document metadata, chunks, flashcards, quiz scores, and academic analytics.
            </p>
            <p>
                We use SQLite for local database operations and Turso for cloud synchronization.
            </p>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 17</span>
            </div>
        </div>

        <!-- ================= PAGE 18 ================= -->
        <div class="page">
            <h1 class="section-title">3. Database Normalization & Relationships</h1>
            <p>
                The schema maps users, documents, chunks, and study metrics:
            </p>
            <pre>
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    file_type TEXT,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY(user_id) REFERENCES users(id)
);
            </pre>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 18</span>
            </div>
        </div>

        <!-- ================= PAGE 19 ================= -->
        <div class="page">
            <h1 class="section-title">3. SQL Commands (DDL vs DML vs DQL)</h1>
            <p>
                DDL statements define the tables, DML statements modify data records, and DQL (SELECT) queries retrieve records:
            </p>
            <pre>
-- Insert new document metadata (DML)
INSERT INTO documents (user_id, filename, file_path) 
VALUES (1, 'syllabus.pdf', '/data/syllabus.pdf');

-- Retrieve documents list (DQL)
SELECT * FROM documents WHERE user_id = 1;
            </pre>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 19</span>
            </div>
        </div>

        <!-- ================= PAGE 20 ================= -->
        <div class="page">
            <h1 class="section-title">3. Advanced SQL Joins & Scoreboard Queries</h1>
            <p>
                We use SQL Joins to display student performance data on the dashboard scoreboard:
            </p>
            <pre>
-- Retrieve top quiz scores for the scoreboard
SELECT username, score, total_questions 
FROM quiz_attempts 
JOIN users ON users.id = quiz_attempts.user_id 
ORDER BY score DESC LIMIT 5;
            </pre>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 20</span>
            </div>
        </div>

        <!-- ================= PAGE 21 ================= -->
        <div class="page">
            <h1 class="section-title">4. Vector Spaces & Transformers</h1>
            <p>
                Semantic searches require vector spaces where distance represents similarity.
            </p>
            <p>
                Converting raw text into dense numerical representations allows us to perform mathematical matching operations on document paragraphs.
            </p>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 21</span>
            </div>
        </div>

        <!-- ================= PAGE 22 ================= -->
        <div class="page">
            <h1 class="section-title">4. all-MiniLM-L6-v2 Embeddings</h1>
            <p>
                We use the `all-MiniLM-L6-v2` transformer model to generate 384-dimensional dense vectors from text chunks.
            </p>
            <pre>
# Python logic to encode text chunks
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(["text chunk"])
            </pre>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 22</span>
            </div>
        </div>

        <!-- ================= PAGE 23 ================= -->
        <div class="page">
            <h1 class="section-title">4. Cosine Similarity & Matrix Math</h1>
            <p>
                Cosine similarity measures the angle between vectors to determine document matches:
            </p>
            <p style="text-align: center; font-weight: bold; margin: 1.5rem 0;">
                Cosine Similarity = (A . B) / (||A|| ||B||)
            </p>
            <p>
                We use NumPy to accelerate these computations, keeping search latency under 8.5ms.
            </p>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 23</span>
            </div>
        </div>

        <!-- ================= PAGE 24 ================= -->
        <div class="page">
            <h1 class="section-title">5. UI/UX & Visualizations</h1>
            <p>
                The UI is designed to reduce visual fatigue during long study sessions, utilizing a glassmorphic dashboard with neutral colors and warm sand backgrounds.
            </p>
            <div class="screenshot-container">
                <img src="file:///E:/Docmind%20ai/frontend/static/assets/categories_screenshot.png" alt="DocMind Categories" class="screenshot-img">
                <div class="screenshot-caption">Figure 5.1: Grid Category Selection Interface</div>
            </div>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 24</span>
            </div>
        </div>

        <!-- ================= PAGE 25 ================= -->
        <div class="page">
            <h1 class="section-title">5. Vis.js Physics Nodes Network</h1>
            <p>
                We use **Vis.js** to render interactive concept networks. Chunks are mapped as nodes, and semantic links are mapped as edges. The physics engine allows students to organize concepts dynamically via drag-and-drop.
            </p>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 25</span>
            </div>
        </div>

        <!-- ================= PAGE 26 ================= -->
        <div class="page">
            <h1 class="section-title">5. CSS 3D active flip layouts</h1>
            <p>
                The study dashboard uses CSS 3D perspective flips for active recall flashcards:
            </p>
            <pre>
/* Card container */
.card-container {
    perspective: 1000px;
}
.card-inner {
    transition: transform 0.6s;
    transform-style: preserve-3d;
}
.card-container:hover .card-inner {
    transform: rotateY(180deg);
}
            </pre>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 26</span>
            </div>
        </div>

        <!-- ================= PAGE 27 ================= -->
        <div class="page">
            <h1 class="section-title">6. Capstone Project: DocMind AI</h1>
            <p>
                DocMind AI was built as a practical application of the data pipelines described. The platform processes documents, creates index vector tables, and generates study aids.
            </p>
            <div class="screenshot-container">
                <img src="file:///E:/Docmind%20ai/frontend/static/assets/dashboard_screenshot.webp" alt="DocMind Dashboard console" class="screenshot-img">
                <div class="screenshot-caption">Figure 6.1: Active Recall Student Dashboard with RAG chat interface</div>
            </div>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 27</span>
            </div>
        </div>

        <!-- ================= PAGE 28 ================= -->
        <div class="page">
            <h1 class="section-title">6. Text Ingestion & Chunker</h1>
            <p>
                `DocumentExtractor` uses PDFPlumber to extract text page-by-page. `TextChunker` segments this text into 1000-character blocks with a 150-character overlap to preserve local context.
            </p>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 28</span>
            </div>
        </div>

        <!-- ================= PAGE 29 ================= -->
        <div class="page">
            <h1 class="section-title">6. Generative Prompting & LLM Fallback</h1>
            <p>
                We construct context-rich prompts using retrieved text chunks. If the similarity score falls below a 0.30 threshold, the query is routed to a general Q&A fallback path.
            </p>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 29</span>
            </div>
        </div>

        <!-- ================= PAGE 30 ================= -->
        <div class="page">
            <h1 class="section-title">6. Spaced Repetition Study Planner</h1>
            <p>
                The study planner helps students schedule review sessions based on Ebbinghaus spaced-repetition intervals, tracking progress on the dashboard scoreboard.
            </p>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 30</span>
            </div>
        </div>

        <!-- ================= PAGE 31 ================= -->
        <div class="page">
            <h1 class="section-title">6. Standard 1-12 School Portal</h1>
            <p>
                The school portal provides grade-appropriate subjects and tools, including a step-by-step math equation solver.
            </p>
            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 31</span>
            </div>
        </div>

    </div>
</body>
</html>
"""

# Write HTML content
try:
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] Created temp report HTML: {temp_html_path}")
except Exception as e:
    print(f"[ERROR] Failed to write HTML: {e}")
    sys.exit(1)

# 5. Render temp_report.html to temp_chapters.pdf using headless Edge
edge_cmd = [
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "--headless",
    "--disable-gpu",
    "--no-sandbox",
    f"--user-data-dir={edge_profile_dir}",
    f"--print-to-pdf={temp_chapters_pdf}",
    temp_html_path
]

try:
    print("Compiling report chapters using headless Edge...")
    result = subprocess.run(edge_cmd, capture_output=True, text=True, timeout=30)
    print(result.stdout)
    if os.path.exists(temp_chapters_pdf):
        print(f"[OK] Compiled temp chapters PDF: {temp_chapters_pdf}")
    else:
        print(f"[ERROR] Failed to compile chapters PDF. Stderr: {result.stderr}")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Edge execution exception: {e}")
    sys.exit(1)

# 6. Merge all PDF files using pypdf PdfWriter
try:
    print("Merging PDFs into final internship report...")
    writer = pypdf.PdfWriter()
    
    # Page 1: First Page PDF
    print(f"Appending Page 1: {first_page_path}")
    reader1 = pypdf.PdfReader(first_page_path)
    for p in reader1.pages:
        writer.add_page(p)
        
    # Page 2: Inplant Certificate of completion PDF
    print(f"Appending Page 2: {temp_inplant_pdf}")
    reader2 = pypdf.PdfReader(temp_inplant_pdf)
    for p in reader2.pages:
        writer.add_page(p)
        
    # Page 3: Project Certificate of completion PDF
    print(f"Appending Page 3: {temp_project_pdf}")
    reader3 = pypdf.PdfReader(temp_project_pdf)
    for p in reader3.pages:
        writer.add_page(p)
        
    # Page 4: Attendance PDF
    print(f"Appending Page 4: {temp_attendance_pdf}")
    reader4 = pypdf.PdfReader(temp_attendance_pdf)
    for p in reader4.pages:
        writer.add_page(p)
        
    # Page 5 onwards: Generated Chapters PDF
    print(f"Appending Page 5 onwards: {temp_chapters_pdf}")
    reader5 = pypdf.PdfReader(temp_chapters_pdf)
    for p in reader5.pages:
        writer.add_page(p)
        
    # Write output
    with open(final_output_path, "wb") as f:
        writer.write(f)
        
    print(f"[SUCCESS] Merged final internship report written to {final_output_path}")
except Exception as e:
    print(f"[ERROR] Failed to merge PDFs: {e}")
    sys.exit(1)

# 7. Cleanup temp files
print("Cleaning up temporary files...")
temp_files = [temp_inplant_pdf, temp_project_pdf, temp_attendance_pdf, temp_html_path, temp_chapters_pdf]
for path in temp_files:
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception as e:
            print(f"[WARNING] Cleanup failed for {path}: {e}")

# Clean up profile dir
if os.path.exists(edge_profile_dir):
    try:
        import shutil
        shutil.rmtree(edge_profile_dir, ignore_errors=True)
    except Exception as e:
        print(f"[WARNING] Profile cleanup failed: {e}")

print("=== COMPILATION COMPLETE ===")
