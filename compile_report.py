import os
import sys
import subprocess
import time
from PIL import Image, ImageDraw, ImageFont
import pypdf

print("=== STARTING INTERNSHIP REPORT COMPILER ===")

workspace_dir = "e:\\Docmind ai"
first_page_path = os.path.join(workspace_dir, "Balaji_Report_FirstPage Copy.pdf")
cert_image_path = os.path.join(workspace_dir, "cropped_IMG20260711205702.jpg")
final_output_path = os.path.join(workspace_dir, "Balaji_Internship_Report.pdf")

# Temporary files paths
temp_cert_pdf = os.path.join(workspace_dir, "temp_cert.pdf")
temp_attendance_pdf = os.path.join(workspace_dir, "temp_attendance.pdf")
temp_html_path = os.path.join(workspace_dir, "temp_report.html")
temp_chapters_pdf = os.path.join(workspace_dir, "temp_chapters.pdf")
edge_profile_dir = os.path.join(workspace_dir, "temp_edge_profile")

# 1. Check first page PDF exists
if not os.path.exists(first_page_path):
    print(f"[ERROR] First page PDF not found at {first_page_path}")
    sys.exit(1)
print(f"[OK] Found first page PDF: {first_page_path}")

# 2. Convert Certificate Image to PDF using Pillow
if not os.path.exists(cert_image_path):
    print(f"[ERROR] Certificate image not found at {cert_image_path}")
    sys.exit(1)
try:
    print("Converting certificate image to PDF...")
    img = Image.open(cert_image_path)
    img.convert('RGB').save(temp_cert_pdf, 'PDF')
    print(f"[OK] Created temp certificate PDF: {temp_cert_pdf}")
except Exception as e:
    print(f"[ERROR] Failed to convert certificate image: {e}")
    sys.exit(1)

# 3. Create clean placeholder PDF for page 3 (Attendance Certificate)
try:
    print("Creating Attendance Certificate placeholder PDF...")
    # Standard A4 size at 300 DPI is 2480 x 3508 pixels
    att_img = Image.new('RGB', (2480, 3508), color='white')
    draw = ImageDraw.Draw(att_img)
    
    draw.rectangle([100, 100, 2380, 3408], outline='#c97f5a', width=10) # Rust border
    draw.rectangle([120, 120, 2360, 3388], outline='#e6dfd5', width=5)  # Light inner border
    
    # Save image directly as PDF
    att_img.save(temp_attendance_pdf, 'PDF')
    print(f"[OK] Created temp attendance placeholder PDF: {temp_attendance_pdf}")
except Exception as e:
    print(f"[ERROR] Failed to create attendance placeholder PDF: {e}")
    sys.exit(1)

# 4. Generate the HTML template for Chapters 1-8
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

        <!-- ================= PAGE 4: CHAPTER 1 - INTRODUCTION TO DOCUMENT INTELLIGENCE ================= -->
        <div class="page">
            <h1 class="section-title">1. Introduction to Document Intelligence</h1>
            <p>
                In today's academic environment, standard keyword search tools (e.g. Ctrl+F) only find exact character matches. If a student searches for "CPU Scheduling latency," a textbook section discussing "Round Robin wait times" will be missed entirely. This failure highlights the need for semantic document retrieval systems.
            </p>
            <p>
                <strong>DocMind AI</strong> is an intelligent document organizer and educational assistant that utilizes Retrieval-Augmented Generation (RAG) to index textbooks semantically. The application automatically maps unit topics to page references, creates study recall aids (quizzes, flashcards), and visualizes connection mind maps.
            </p>
            <h3 class="block-title">Key Core Goals:</h3>
            <ul>
                <li><strong>Syllabus Mapping:</strong> Match unit syllabus text to document pages using vector similarity.</li>
                <li><strong>Interactive Study Decks:</strong> Generate 3D active recall flashcards and cognitive quizzes.</li>
                <li><strong>Dynamic Network Mapping:</strong> Visualize textbook connections in interactive maps.</li>
            </ul>

            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 4</span>
            </div>
        </div>

        <!-- ================= PAGE 5: CHAPTER 2 - PYTHON FOR AI & DATA MANIPULATION ================= -->
        <div class="page">
            <h1 class="section-title">2. Python for AI & Data Manipulation</h1>
            <p>
                Python is the primary language used to build DocMind AI due to its clear syntax and extensive scientific libraries. Essential programming structures implemented in our RAG pipeline include:
            </p>
            
            <h2 class="sub-section-title">2.1 Python Collections & Data Handling</h2>
            <ul>
                <li><strong>Lists:</strong> Used to maintain chronological page records and ordered text paragraphs.</li>
                <li><strong>Dictionaries:</strong> Used to cache vector metadata mapping, key-value configurations, and JSON-based API payloads.</li>
                <li><strong>Sets:</strong> Employed to filter unique keywords and remove stopwords.</li>
            </ul>

            <h2 class="sub-section-title">2.2 Control Flow & Functions</h2>
            <p>
                Loops (`for` and `while`) iterate through document chunks, calling modular functions to extract text, calculate vector representations, and clean punctuation marks.
            </p>
            <pre>
# Example control flow: Filtering stopwords from keywords list
filtered_words = []
for word in words:
    if word not in stopwords and len(word) > 3:
        filtered_words.append(word)
            </pre>

            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 5</span>
            </div>
        </div>

        <!-- ================= PAGE 6: CHAPTER 3 - RELATIONAL DATABASES & SQL COMMANDS ================= -->
        <div class="page">
            <h1 class="section-title">3. Relational Databases & SQL Commands</h1>
            <p>
                DocMind AI uses a relational database schema to persist student credentials, document metadata, chunks, flashcards, quiz scores, and academic analytics.
            </p>

            <h2 class="sub-section-title">3.1 Database Schema considerations</h2>
            <p>
                The schema includes:
            </p>
            <ul>
                <li><strong>users:</strong> Stores ID, username, email, and password hashes.</li>
                <li><strong>documents:</strong> Maps user ID to specific filenames, paths, size, and status.</li>
                <li><strong>document_chunks:</strong> Stores document chunks with page references.</li>
                <li><strong>study_quizzes:</strong> Retains generated MCQ assessment question banks.</li>
            </ul>

            <h2 class="sub-section-title">3.2 SQL DDL & DQL Commands</h2>
            <p>
                DDL statements define the tables. DQL (SELECT) queries retrieve matching records:
            </p>
            <pre>
-- Retrieve top 5 quiz scores for scoreboard dashboard
SELECT username, score, total_questions 
FROM quiz_attempts 
JOIN users ON users.id = quiz_attempts.user_id 
ORDER BY score DESC LIMIT 5;
            </pre>

            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 6</span>
            </div>
        </div>

        <!-- ================= PAGE 7: CHAPTER 4 - VECTOR SPACES & EMBEDDINGS ================= -->
        <div class="page">
            <h1 class="section-title">4. Vector Spaces & Embeddings</h1>
            <p>
                To search paragraphs semantically, namba code turns raw text strings into dense vector representations.
            </p>

            <h2 class="sub-section-title">4.1 all-MiniLM-L6-v2 Embeddings Model</h2>
            <p>
                The local pipeline utilizes the pre-trained `all-MiniLM-L6-v2` transformer model to convert each text chunk into a 384-dimensional array of float values. This model runs locally on the CPU, with an API fallback if internet connectivity is available.
            </p>

            <h2 class="sub-section-title">4.2 Cosine Similarity Math</h2>
            <p>
                The semantic distance between a user query vector and paragraph vectors is calculated using the cosine similarity formula:
            </p>
            <p style="text-align: center; font-weight: bold; margin: 1.5rem 0;">
                Cosine Similarity = (A . B) / (||A|| ||B||)
            </p>
            <p>
                Numpy executes these vector calculations efficiently, keeping latency under 8.5ms.
            </p>

            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 7</span>
            </div>
        </div>

        <!-- ================= PAGE 8: CHAPTER 5 - DYNAMIC VISUALIZATIONS ================= -->
        <div class="page">
            <h1 class="section-title">5. Dynamic Visualizations & UI Dashboards</h1>
            <p>
                Data visualizations help students understand complex concepts and organize their study materials.
            </p>

            <h2 class="sub-section-title">5.1 Vis.js Concept Node Graphs</h2>
            <p>
                Concept connections are visualized using **Vis.js**, an interactive, canvas-based network visualization engine. Chunks are mapped as nodes, and semantic links are mapped as edges. The physics engine allows students to organize concepts dynamically via drag-and-drop.
            </p>

            <h2 class="sub-section-title">5.2 Interactive recall Dashboards</h2>
            <p>
                The UI uses CSS 3D flips for flashcards, glassmorphism templates, and interactive scoreboards. These templates are designed to be clean and modern.
            </p>

            <div class="screenshot-container">
                <img src="file:///E:/Docmind%20ai/frontend/static/assets/categories_screenshot.png" alt="DocMind Categories" class="screenshot-img">
                <div class="screenshot-caption">Figure 5.1: Category Portal selection dashboard</div>
            </div>

            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 8</span>
            </div>
        </div>

        <!-- ================= PAGE 9: CHAPTER 6 - CAPSTONE PROJECT IMPLEMENTATION ================= -->
        <div class="page">
            <h1 class="section-title">6. Capstone Project: DocMind AI</h1>
            <p>
                As a practical application of these data pipelines, **DocMind AI** was built. The platform processes documents, performs vector indexing, and renders educational resources.
            </p>

            <h2 class="sub-section-title">6.1 PDF Ingestion & Chunker</h2>
            <p>
                `DocumentExtractor` reads text layouts, and `TextChunker` groups text into overlapping paragraphs of 1000 characters to maintain context.
            </p>

            <div class="screenshot-container">
                <img src="file:///E:/Docmind%20ai/frontend/static/assets/hero_screenshot.png" alt="DocMind Hero Landing" class="screenshot-img">
                <div class="screenshot-caption">Figure 6.1: Brand Landing Page redesign</div>
            </div>

            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 9</span>
            </div>
        </div>

        <!-- ================= PAGE 10: CHAPTER 6 - CAPSTONE CONTINUED ================= -->
        <div class="page">
            <h1 class="section-title">6. Implemented Modules (Continued)</h1>
            
            <h2 class="sub-section-title">6.2 Vector Search Q&A Engine</h2>
            <p>
                Compares the user query embedding against stored paragraph vectors. Chunks with similarity scores above a 0.30 threshold are retrieved as context. If the best score falls below 0.30, the system falls back to general Q&A.
            </p>

            <h2 class="sub-section-title">6.3 3D Recall & Quizzes</h2>
            <p>
                Retrieves definitions to generate flashcard decks and creates MCQ quizzes categorized by Bloom's Taxonomy.
            </p>

            <div class="screenshot-container">
                <img src="file:///E:/Docmind%20ai/frontend/static/assets/dashboard_screenshot.webp" alt="DocMind Dashboard console" class="screenshot-img">
                <div class="screenshot-caption">Figure 6.2: Glassmorphic Student Dashboard with RAG chat interface</div>
            </div>

            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 10</span>
            </div>
        </div>

        <!-- ================= PAGE 11: CHAPTER 7 - CONCLUSION & LEARNINGS ================= -->
        <div class="page">
            <h1 class="section-title">7. Conclusion & Internship Learnings</h1>
            <p>
                The academic internship at <strong>CodeBind Technologies, Chennai</strong> provided practical experience in building AIML architectures and document search engines.
            </p>
            <p>
                The development of **DocMind AI** successfully proved that RAG pipelines can automate textbook indexing and study support. Participating in the Data Science workshop and completing the Corporate Training test also improved skills in data structure design and engineering logic.
            </p>
            <h3 class="block-title">Key Technical Outcomes:</h3>
            <ul>
                <li>Developed a high-speed Python text ingestion and chunking pipeline.</li>
                <li>Mapped textbook pages to course syllabus units using cosine similarity.</li>
                <li>Designed responsive dashboards with 3D flashcards and vis.js graphs.</li>
            </ul>

            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 11</span>
            </div>
        </div>

        <!-- ================= PAGE 12: CHAPTER 8 - REFERENCES ================= -->
        <div class="page">
            <h1 class="section-title">8. References</h1>
            <h3 class="block-title">Sentence-Transformers documentation</h3>
            <p>SentenceTransformers. "all-MiniLM-L6-v2 model card." https://sbert.net/. Reference guide for generating text embeddings.</p>
            
            <h3 class="block-title">Flask Web Framework</h3>
            <p>Pallets Projects. "Flask Documentation." https://flask.palletsprojects.com/. Reference guide for routing REST APIs.</p>

            <h3 class="block-title">NumPy Vector Math</h3>
            <p>NumPy. "Numpy Multi-Dimensional Arrays." https://numpy.org/. Reference guide for dot-products and vector norms calculations.</p>

            <h3 class="block-title">PDFPlumber Character Parsing</h3>
            <p>PDFPlumber. "PDFPlumber Repository." https://github.com/jsvine/pdfplumber. Reference guide for extracting text layouts from PDFs.</p>
            
            <p style="margin-top: 4rem; text-align: center; font-style: italic; color: #8c827a;">
                --- End of Academic Report ---
            </p>

            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 12</span>
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
        
    # Page 2: Certificate of completion PDF
    print(f"Appending Page 2: {temp_cert_pdf}")
    reader2 = pypdf.PdfReader(temp_cert_pdf)
    for p in reader2.pages:
        writer.add_page(p)
        
    # Page 3: Attendance placeholder PDF
    print(f"Appending Page 3: {temp_attendance_pdf}")
    reader3 = pypdf.PdfReader(temp_attendance_pdf)
    for p in reader3.pages:
        writer.add_page(p)
        
    # Page 4 onwards: Generated Chapters PDF
    print(f"Appending Page 4 onwards: {temp_chapters_pdf}")
    reader4 = pypdf.PdfReader(temp_chapters_pdf)
    for p in reader4.pages:
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
temp_files = [temp_cert_pdf, temp_attendance_pdf, temp_html_path, temp_chapters_pdf]
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
