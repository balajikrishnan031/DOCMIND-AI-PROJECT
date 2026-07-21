import json
import time
from typing import Dict, List, Any

class ExecutiveExportEngine:
    """
    Enterprise Academic Export & Reporting Engine for DocMind AI.
    Generates downloadable Markdown and HTML executive reports containing
    syllabus topic-to-page mappings, flashcards, quiz analytics, and accreditation status.
    """

    @staticmethod
    def generate_markdown_report(
        document_title: str,
        grade: str,
        role: str,
        syllabus_units: List[Dict[str, Any]],
        flashcards: List[Dict[str, str]],
        quiz_attempts: List[Dict[str, Any]]
    ) -> str:
        """
        Generates a comprehensive Markdown Executive Summary Report.
        """
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        
        md_content = []
        md_content.append(f"# DocMind AI - Executive Academic Report")
        md_content.append(f"**Document Title:** {document_title}")
        md_content.append(f"**Academic Tier:** {grade} | **Audience Role:** {role}")
        md_content.append(f"**Report Generated:** {timestamp_str}")
        md_content.append(f"\n---\n")

        # 1. Syllabus Unit Mapping
        md_content.append(f"## 1. Semantic Syllabus & Textbook Page Mapping")
        if syllabus_units:
            for u in syllabus_units:
                md_content.append(f"### {u.get('unit_title', 'Unit')}")
                topics = u.get('topics', [])
                if topics:
                    for t in topics:
                        t_name = t.get('topic_name', 'Topic')
                        pg = t.get('page_number', 1)
                        md_content.append(f"- **{t_name}** -> Textbook Page: **{pg}**")
                else:
                    md_content.append(f"- *No specific topics mapped yet.*")
        else:
            md_content.append(f"- *Syllabus units indexed automatically via RAG vector search.*")

        md_content.append(f"\n---\n")

        # 2. 3D Recall Flashcards Summary
        md_content.append(f"## 2. Active Recall Flashcards Deck")
        if flashcards:
            for idx, fc in enumerate(flashcards, 1):
                md_content.append(f"**Card {idx}:** {fc.get('front', '')}")
                md_content.append(f"> *Answer:* {fc.get('back', '')}\n")
        else:
            md_content.append(f"- *Flashcard deck generated upon document processing.*")

        md_content.append(f"\n---\n")

        # 3. Practice Exam Performance
        md_content.append(f"## 3. Practice Exam & Quiz Attempts History")
        if quiz_attempts:
            for att in quiz_attempts:
                score = att.get('score', 0)
                total = att.get('total', 5)
                pct = (score / total) * 100.0 if total > 0 else 0
                md_content.append(f"- Attempt Date: {att.get('attempted_at', 'Recent')} | Score: **{score}/{total}** ({pct:.1f}%)")
        else:
            md_content.append(f"- *No exam attempts logged yet.*")

        md_content.append(f"\n---\n")
        md_content.append(f"*Report compiled by DocMind AI Executive Engine.*")

        return "\n".join(md_content)

    @staticmethod
    def generate_html_print_report(markdown_report: str) -> str:
        """
        Wraps Markdown content into a print-optimized, glassmorphic HTML document.
        """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DocMind AI - Academic Executive Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 40px; background: #0f172a; color: #f8fafc; line-height: 1.6; }}
        h1 {{ color: #38bdf8; border-bottom: 2px solid #38bdf8; padding-bottom: 10px; }}
        h2 {{ color: #c084fc; margin-top: 30px; }}
        h3 {{ color: #fbbf24; }}
        blockquote {{ background: rgba(255,255,255,0.05); border-left: 4px solid #38bdf8; padding: 10px 15px; margin: 10px 0; }}
        hr {{ border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 30px 0; }}
    </style>
</head>
<body>
    <pre style="white-space: pre-wrap; font-family: inherit;">{markdown_report}</pre>
</body>
</html>"""
