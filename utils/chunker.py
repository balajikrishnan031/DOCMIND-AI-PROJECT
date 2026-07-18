import re

class TextChunker:
    @staticmethod
    def chunk_document(extracted_pages, chunk_size=700, overlap=120):
        """
        Groups words and sentences into small semantic chunks of approx `chunk_size` characters,
        with an overlap of `overlap` characters. Keeps track of original page numbers.
        """
        chunks = []
        chunk_idx = 0
        
        for page_data in extracted_pages:
            page_num = page_data["page"]
            text = page_data["text"]
            
            # Split text by paragraphs, fallback to sentences
            paragraphs = re.split(r'\n+', text)
            
            current_chunk = ""
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                
                # If paragraph itself is larger than chunk_size, split it by sentence
                if len(para) > chunk_size:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    for sent in sentences:
                        sent = sent.strip()
                        if not sent:
                            continue
                        
                        if len(current_chunk) + len(sent) + 1 <= chunk_size:
                            current_chunk += (" " if current_chunk else "") + sent
                        else:
                            if current_chunk:
                                chunks.append((chunk_idx, page_num, current_chunk))
                                chunk_idx += 1
                                # Keep the end of the current chunk as overlap
                                current_chunk = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                            current_chunk += (" " if current_chunk else "") + sent
                else:
                    if len(current_chunk) + len(para) + 1 <= chunk_size:
                        current_chunk += ("\n" if current_chunk else "") + para
                    else:
                        if current_chunk:
                            chunks.append((chunk_idx, page_num, current_chunk))
                            chunk_idx += 1
                            current_chunk = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                        current_chunk += ("\n" if current_chunk else "") + para
            
            # Add any remaining text
            if current_chunk:
                chunks.append((chunk_idx, page_num, current_chunk))
                chunk_idx += 1
                
        return chunks
