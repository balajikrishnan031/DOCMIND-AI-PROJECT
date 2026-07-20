import re

class SyllabusParser:
    @staticmethod
    def parse_syllabus(text_pages):
        """
        Processes text pages from a syllabus PDF, identifying structural units (e.g., UNIT I, UNIT II)
        and parsing line-by-line or comma-separated topic titles.
        Returns a dictionary representing the syllabus structure:
        {
           1: {"title": "UNIT I: Introduction", "topics": ["Machine Learning", "Regression", ...]},
           2: ...
        }
        """
        full_text = "\n".join([page["text"] for page in text_pages])
        
        # 1. Regex to split into units
        # Matches patterns like "UNIT I", "UNIT - 1", "UNIT 2", "MODULE I", etc.
        unit_regex = r"\b(?:UNIT|MODULE)\s*[-:]*\s*([IVXLCDM\d]+)\b"
        
        # Find all match positions of unit boundaries
        matches = list(re.finditer(unit_regex, full_text, re.IGNORECASE))
        
        syllabus_data = {}
        
        if not matches:
            # Fallback if no explicit "UNIT" borders found:
            # Create a single generic unit and split text into logical lines
            lines = [l.strip() for l in full_text.split('\n') if len(l.strip()) > 15 and len(l.strip()) < 80]
            syllabus_data[1] = {
                "title": "General Syllabus Topics",
                "topics": lines[:15] # limit to top 15
            }
            return syllabus_data
            
        for i, match in enumerate(matches):
            unit_index = i + 1
            unit_num_str = match.group(1)
            
            # Start position is the match header
            start_pos = match.start()
            # End position is either the next match start or end of text
            end_pos = matches[i+1].start() if i + 1 < len(matches) else len(full_text)
            
            # Get full text block for this unit
            unit_block = full_text[start_pos:end_pos].strip()
            
            # Extract the first line as the Unit title
            lines = [l.strip() for l in unit_block.split('\n') if l.strip()]
            unit_title = lines[0] if lines else f"UNIT {unit_num_str}"
            
            # Extract topics from the remaining lines of the block
            remaining_text = " ".join(lines[1:]) if len(lines) > 1 else ""
            
            # Syllabus topics are often separated by commas, semicolons, or dashes
            # Let's split by standard separators
            parts = re.split(r'[,;\-\–\—\n]', remaining_text)
            topics = []
            for p in parts:
                p_clean = p.strip()
                # A good topic is between 10 and 70 characters long and contains words
                if 8 < len(p_clean) < 80 and not re.match(r'^(?:page|course|credits|hours|syllabus|reference|textbook)', p_clean, re.IGNORECASE):
                    # Clean double whitespaces
                    p_clean = re.sub(r'\s+', ' ', p_clean)
                    topics.append(p_clean)
                    
            syllabus_data[unit_index] = {
                "title": unit_title,
                "topics": topics[:12] # Limit to 12 topics per unit to avoid UI overload
            }
            
        return syllabus_data
