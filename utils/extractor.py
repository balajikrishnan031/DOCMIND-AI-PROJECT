import os
import pdfplumber
from pypdf import PdfReader
import docx

class DocumentExtractor:
    @staticmethod
    def extract_pdf(file_path):
        """
        Extracts text from PDF, returning a list of dicts:
        [{"page": 1, "text": "..."}]
        Uses pdfplumber primarily and falls back to pypdf.
        """
        pages = []
        try:
            # Attempt to use pdfplumber for cleaner text extraction
            with pdfplumber.open(file_path) as pdf:
                for idx, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        pages.append({
                            "page": idx + 1,
                            "text": text.strip()
                        })
            
            # Fallback to pypdf if pdfplumber extracted nothing
            if not pages:
                print("pdfplumber extracted empty content, falling back to pypdf.")
                reader = PdfReader(file_path)
                for idx, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        pages.append({
                            "page": idx + 1,
                            "text": text.strip()
                        })
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            # Try pypdf directly as emergency fallback
            try:
                reader = PdfReader(file_path)
                for idx, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        pages.append({
                            "page": idx + 1,
                            "text": text.strip()
                        })
            except Exception as ex:
                print(f"Emergency PDF extraction fallback failed: {ex}")
                
        return pages

    @staticmethod
    def extract_docx(file_path):
        """
        Extracts text from DOCX files, approximating pages based on paragraph chunks.
        """
        pages = []
        try:
            doc = docx.Document(file_path)
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            
            # Since word docs don't have hard-coded page boundaries, 
            # we group every ~8 paragraphs together as a "page".
            chunk_size = 8
            for idx in range(0, len(paragraphs), chunk_size):
                page_text = "\n".join(paragraphs[idx : idx + chunk_size])
                pages.append({
                    "page": (idx // chunk_size) + 1,
                    "text": page_text
                })
        except Exception as e:
            print(f"Error extracting DOCX: {e}")
        return pages

    @staticmethod
    def extract_txt(file_path):
        """
        Extracts text from plain text files, splitting into estimated "pages" of ~2500 characters.
        """
        pages = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()
                
            page_char_limit = 2500
            for idx in range(0, len(content), page_char_limit):
                page_text = content[idx : idx + page_char_limit]
                pages.append({
                    "page": (idx // page_char_limit) + 1,
                    "text": page_text
                })
        except Exception as e:
            print(f"Error extracting TXT: {e}")
        return pages

    @classmethod
    def extract(cls, file_path):
        """
        Main entry point for extracting text. Dispatches based on file extension.
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return cls.extract_pdf(file_path)
        elif ext == '.docx':
            return cls.extract_docx(file_path)
        elif ext in ['.txt', '.md']:
            return cls.extract_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
