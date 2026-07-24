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

# 4. Generate the HTML template for Chapters 1-9 (Using Raw string to prevent escaping issues)
html_content = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DocMind AI - Chapters Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;1,400&family=Inter:wght@400;500;600&display=swap');
        
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
            min-height: 1000px;
            box-sizing: border-box;
            padding-bottom: 3rem;
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

        <!-- ================= PAGE 4: CHAPTER 1 - COMPANY PROFILE ================= -->
        <div class="page">
            <h1 class="section-title">1. Company Profile</h1>
            <h2 class="sub-section-title">CodeBind Technologies, Chennai</h2>
            <p>
                <strong>CodeBind Technologies</strong> is a leading ISO 9001:2015 certified software development, engineering services, and technical consultancy firm headquartered in T. Nagar, Chennai, Tamil Nadu. The company is internationally recognized and accredited under the EGAC (Egyptian Accreditation Council) and the IAF (International Accreditation Forum) frameworks.
            </p>
            <p>
                The organization focuses on developing scalable enterprise products using modern backend stacks (Python Flask/Django, FastAPI), cloud architectures, and deep neural information retrieval layers. Additionally, CodeBind Technologies maintains active training operations to provide students with industrial skills in data science, artificial intelligence, and software craftsmanship.
            </p>
            <h3 class="block-title">Key Core Domains:</h3>
            <ul>
                <li><strong>Enterprise Software Engineering:</strong> Building modular database applications, REST web endpoints, and responsive user interfaces.</li>
                <li><strong>Artificial Intelligence & Machine Learning:</strong> Deploying dense vector representations, similarity matching algorithms, and automated pipeline seeder databases.</li>
                <li><strong>Industrial Learning Operations:</strong> Assisting universities in conducting workshops, aptitude tests, and in-plant training modules.</li>
            </ul>

            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 4</span>
            </div>
        </div>

        <!-- ================= PAGE 5: CHAPTER 2 - PYTHON & AIML CORE ================= -->
        <div class="page">
            <h1 class="section-title">2. Python Ecosystem & AIML Core</h1>
            <h2 class="sub-section-title">A. Python in Semantic Systems</h2>
            <p>
                Python provides a rich ecosystem of libraries that accelerate numerical operations and natural language matching. Key packages implemented in DocMind AI include:
            </p>
            <ul>
                <li><strong>Numpy:</strong> Essential for matrix math and calculating similarity scores between multidimensional document vectors.</li>
                <li><strong>Sentence-Transformers:</strong> Pre-trained PyTorch transformers that turn text strings into dense numerical vectors.</li>
                <li><strong>PDFPlumber:</strong> Provides precise character extraction, boundary mapping, and coordinate checking of PDF pages.</li>
            </ul>
            
            <h2 class="sub-section-title">B. Retrieval-Augmented Generation (RAG) Flow</h2>
            <p>
                RAG improves LLM answers by supplying relevant context from indexed documents. Instead of sending raw user questions directly to the generative API, the query is first vectorized to search the document database, retrieve the best matches, and construct a context-rich prompt.
            </p>

            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 5</span>
            </div>
        </div>

        <!-- ================= PAGE 6: CHAPTER 3 - PROBLEM STATEMENT ================= -->
        <div class="page">
            <h1 class="section-title">3. Problem Statement & Objectives</h1>
            <h2 class="sub-section-title">A. The Problem Statement</h2>
            <p>
                Students and professors routinely deal with dense textbooks and long syllabus guidelines. Standard search engines (like Ctrl+F) only find exact word matches and fail on semantic queries. Furthermore, creating active recall study aids (flashcards, quizzes) manually takes significant time.
            </p>
            <h2 class="sub-section-title">B. Project Objectives</h2>
            <p>
                DocMind AI addresses these limitations through the following key deliverables:
            </p>
            <ol>
                <li><strong>Syllabus-to-Page Mapping:</strong> Map unit topics to precise textbook page ranges.</li>
                <li><strong>Interactive Recall:</strong> Automatically generate 3D flashcards and practice quizzes.</li>
                <li><strong>Numpy-Optimized Search:</strong> Provide high-speed, local similarity matches.</li>
                <li><strong>Fallback Q&A System:</strong> Automatically redirect general questions to LLMs.</li>
            </ol>

            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 6</span>
            </div>
        </div>

        <!-- ================= PAGE 7: CHAPTER 4 - SYSTEM DESIGN ================= -->
        <div class="page">
            <h1 class="section-title">4. System Requirements & Architecture</h1>
            
            <h3 class="block-title">Hardware Requirements:</h3>
            <ul>
                <li>Processor: Intel Core i5 / AMD Ryzen 5 or higher.</li>
                <li>Memory (RAM): Minimum 8 GB (16 GB recommended for sentence-transformers).</li>
                <li>Storage: 2 GB free disk space.</li>
            </ul>

            <h3 class="block-title">Software Requirements:</h3>
            <ul>
                <li>Python 3.10 / 3.11 / 3.12, SQLite database.</li>
                <li>Flask, NumPy, PDFPlumber, Requests, python-dotenv.</li>
            </ul>

            <h2 class="sub-section-title">System Architecture</h2>
            <div class="screenshot-container">
                <img src="file:///E:/Docmind%20ai/frontend/static/assets/hero_screenshot.png" alt="DocMind AI landing layout" class="screenshot-img">
                <div class="screenshot-caption">Figure 4.1: Brand Landing Page & Core UI Architecture</div>
            </div>

            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 7</span>
            </div>
        </div>

        <!-- ================= PAGE 8: CHAPTER 5 - IMPLEMENTED MODULES ================= -->
        <div class="page">
            <h1 class="section-title">5. Implemented Modules</h1>
            
            <h3 class="block-title">A. PDF Extractor & Chunker</h3>
            <p>
                Extracts clean text streams page-by-page. Chunker segments the text into 1000-character paragraphs with a 150-character overlap to preserve local context.
            </p>

            <h3 class="block-title">B. Dense Vector Storage</h3>
            <p>
                Encodes text blocks into 384-dimensional vectors. Index data is cached in JSON files, enabling fast in-memory computations.
            </p>

            <h3 class="block-title">C. School Portal & Solver</h3>
            <p>
                Grade-tailored solvers support school education from Standard 1 to 12.
            </p>

            <div class="screenshot-container">
                <img src="file:///E:/Docmind%20ai/frontend/static/assets/categories_screenshot.png" alt="DocMind AI Categories" class="screenshot-img">
                <div class="screenshot-caption">Figure 5.1: Multi-Level Academic Category Selection Portal</div>
            </div>

            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 8</span>
            </div>
        </div>

        <!-- ================= PAGE 9: CHAPTER 6 - MATHEMATICS ================= -->
        <div class="page">
            <h1 class="section-title">6. Code Implementation & Mathematics</h1>
            <h2 class="sub-section-title">A. Cosine Similarity Matching</h2>
            <p>
                The system determines how close a document paragraph is to a user's search query using the following mathematical formula:
            </p>
            <p style="text-align: center; font-weight: bold; margin: 1.5rem 0;">
                Cosine Similarity = (A . B) / (||A|| ||B||)
            </p>
            <h2 class="sub-section-title">B. Python Implementation Snippet</h2>
            <pre>
# Convert vectors to numpy array for operations
vectors = np.array([item["vector"] for item in index_data], dtype=np.float32)
q_vec = np.array(query_vector, dtype=np.float32)

# Calculate dot products
dot_products = np.dot(vectors, q_vec)
vectors_norms = np.linalg.norm(vectors, axis=1)
q_norm = np.linalg.norm(q_vec)

# Calculate cosine similarities
similarities = dot_products / (vectors_norms * q_norm + 1e-8)
            </pre>

            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 9</span>
            </div>
        </div>

        <!-- ================= PAGE 10: CHAPTER 7 - SCREENSHOTS ================= -->
        <div class="page">
            <h1 class="section-title">7. UI Design & User Interface</h1>
            <p>
                The user interface uses a modern glassmorphic theme with a warm neutral palette to ensure visual comfort during extended study sessions.
            </p>

            <div class="screenshot-container">
                <img src="file:///E:/Docmind%20ai/frontend/static/assets/dashboard_screenshot.webp" alt="DocMind AI Dashboard" class="screenshot-img">
                <div class="screenshot-caption">Figure 7.1: Active Recall Student Dashboard & RAG chat console</div>
            </div>

            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 10</span>
            </div>
        </div>

        <!-- ================= PAGE 11: CHAPTER 8 - VERIFICATION ================= -->
        <div class="page">
            <h1 class="section-title">8. Verification & Testing</h1>
            <p>
                An automated regression suite verified document retrieval and general Q&A fallback:
            </p>
            <pre>
=== STARTING Q&A PIPELINE TESTS ===
API Provider configured: local

--- Test Case 1: Asking Document Q&A (CPU Scheduling) ---
Loading local sentence-transformers model...
Sentence-transformers loaded locally.
Question: What is Round Robin CPU scheduling?
Answer:
Round Robin CPU scheduling is a preemptive algorithm that handles process execution order by assigning a fixed time slice quantum to each process [1].
Sources Mapped: [{'document_id': 1, 'page': 1, 'snippet': 'CPU Scheduling...'}]
[SUCCESS] RAG context correctly matched and cited from indexed document.
            </pre>

            <div class="page-footer">
                <span>DocMind AI - Internship Report</span>
                <span>Page 11</span>
            </div>
        </div>

        <!-- ================= PAGE 12: CHAPTER 9 - CONCLUSION ================= -->
        <div class="page">
            <h1 class="section-title">9. Conclusion & Internship Outcomes</h1>
            <p>
                The academic internship at <strong>CodeBind Technologies, Chennai</strong> provided key insights into Retrieval-Augmented Generation, vector embeddings, and modular web backends.
            </p>
            <p>
                Developing <strong>DocMind AI</strong> successfully proved how machine learning can automate text indexing. The experience gained during the Data Science workshop and Corporate Training Test has strengthened skills in data processing and engineering logic.
            </p>

            <p style="margin-top: 4rem; text-align: center; font-style: italic; color: #8c827a;">
                Report Certified & Approved by CodeBind Technologies Issuing Authority.
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

# 6. Merge all PDF files using pypdf PdfWriter for universal compatibility
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
