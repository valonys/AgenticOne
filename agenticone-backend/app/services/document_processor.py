"""
Document Processor Service for handling various document types
"""
import io
import mimetypes
from typing import Dict, List, Any, Optional
from datetime import datetime

class DocumentProcessor:
    """Document processor for various file types"""
    
    def __init__(self):
        self.supported_types = {
            "application/pdf": self._process_pdf,
            "image/jpeg": self._process_image,
            "image/png": self._process_image,
            "image/tiff": self._process_image,
            "text/plain": self._process_text,
            "application/msword": self._process_doc,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": self._process_docx,
        }
        self.status = "initialized"
    
    async def process_document(
        self, 
        content: bytes, 
        filename: str, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a document and extract content"""
        try:
            # Detect document type
            document_type = self._detect_document_type(filename, content)
            
            # Process based on type
            if document_type in self.supported_types:
                processor = self.supported_types[document_type]
                result = await processor(content, filename, metadata)
            else:
                # Fallback to text processing
                result = await self._process_text(content, filename, metadata)
            
            # Add metadata
            result.update({
                "document_type": document_type,
                "filename": filename,
                "size": len(content),
                "processed_at": datetime.utcnow().isoformat()
            })
            
            return result
            
        except Exception as e:
            raise ValueError(f"Failed to process document: {str(e)}")
    
    def _detect_document_type(self, filename: str, content: bytes) -> str:
        """Detect document type from filename and content"""
        try:
            # Try to detect from filename
            mime_type, _ = mimetypes.guess_type(filename)
            if mime_type:
                return mime_type
            
            # Fallback to content-based detection
            if content.startswith(b'%PDF'):
                return "application/pdf"
            elif content.startswith(b'\xff\xd8\xff'):
                return "image/jpeg"
            elif content.startswith(b'\x89PNG'):
                return "image/png"
            elif content.startswith(b'II*\x00') or content.startswith(b'MM\x00*'):
                return "image/tiff"
            else:
                return "text/plain"
                
        except Exception:
            return "text/plain"
    
    async def _process_pdf(self, content: bytes, filename: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process PDF documents"""
        try:
            # In production, you would use PyPDF2, pdfplumber, or similar
            # For now, we'll create a mock implementation
            text_content = f"PDF content from {filename}\n\nThis is a mock PDF processing result."
            
            # Extract metadata
            pdf_metadata = {
                "pages": 1,  # Mock page count
                "title": filename,
                "author": "Unknown",
                "created": datetime.utcnow().isoformat()
            }
            
            return {
                "text": text_content,
                "metadata": {**metadata, **pdf_metadata},
                "images": [],  # Would extract images in production
                "tables": []   # Would extract tables in production
            }
            
        except Exception as e:
            raise ValueError(f"Failed to process PDF: {str(e)}")
    
    async def _process_image(self, content: bytes, filename: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process image documents"""
        try:
            # In production, you would use PIL, OpenCV, or similar
            # For now, we'll create a mock implementation
            text_content = f"Image content from {filename}\n\nThis is a mock image processing result."
            
            # Extract image metadata
            image_metadata = {
                "format": filename.split('.')[-1].lower(),
                "size": len(content),
                "dimensions": "Unknown"  # Would extract in production
            }
            
            return {
                "text": text_content,
                "metadata": {**metadata, **image_metadata},
                "images": [{"filename": filename, "content": content}],
                "tables": []
            }
            
        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")
    
    async def _process_text(self, content: bytes, filename: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process text documents"""
        try:
            # Decode text content
            text_content = content.decode('utf-8', errors='ignore')
            
            return {
                "text": text_content,
                "metadata": metadata,
                "images": [],
                "tables": []
            }
            
        except Exception as e:
            raise ValueError(f"Failed to process text: {str(e)}")
    
    async def _process_doc(self, content: bytes, filename: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process DOC documents"""
        try:
            # In production, you would use python-docx or similar
            # For now, we'll create a mock implementation
            text_content = f"DOC content from {filename}\n\nThis is a mock DOC processing result."
            
            return {
                "text": text_content,
                "metadata": {**metadata, "format": "doc"},
                "images": [],
                "tables": []
            }
            
        except Exception as e:
            raise ValueError(f"Failed to process DOC: {str(e)}")
    
    async def _process_docx(self, content: bytes, filename: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process DOCX documents"""
        try:
            # In production, you would use python-docx
            # For now, we'll create a mock implementation
            text_content = f"DOCX content from {filename}\n\nThis is a mock DOCX processing result."
            
            return {
                "text": text_content,
                "metadata": {**metadata, "format": "docx"},
                "images": [],
                "tables": []
            }
            
        except Exception as e:
            raise ValueError(f"Failed to process DOCX: {str(e)}")
    
    async def generate_summary(self, content: str, max_length: int = 500) -> str:
        """Generate a summary of the document content"""
        try:
            # In production, you would use a proper summarization model
            # For now, we'll create a simple extractive summary
            sentences = content.split('.')
            if len(sentences) <= 3:
                return content
            
            # Simple extractive summary (first few sentences)
            summary_sentences = sentences[:3]
            summary = '. '.join(summary_sentences) + '.'
            
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            
            return summary
            
        except Exception as e:
            return f"Summary generation failed: {str(e)}"
    
    async def extract_keywords(self, content: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from document content"""
        try:
            # Simple keyword extraction (in production, use proper NLP)
            words = content.lower().split()
            
            # Remove common stop words
            stop_words = {
                "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
                "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", 
                "has", "had", "do", "does", "did", "will", "would", "could", "should"
            }
            
            # Filter and count words
            filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
            word_count = {}
            for word in filtered_words:
                word_count[word] = word_count.get(word, 0) + 1
            
            # Sort by frequency and return top keywords
            sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
            keywords = [word for word, count in sorted_words[:max_keywords]]
            
            return keywords
            
        except Exception as e:
            return []
    
    async def extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """Extract tables from document content"""
        try:
            # In production, you would use proper table extraction
            # For now, we'll create a mock implementation
            tables = []
            
            # Simple table detection (look for patterns)
            lines = content.split('\n')
            current_table = []
            
            for line in lines:
                if '|' in line or '\t' in line:
                    current_table.append(line.strip())
                elif current_table:
                    if len(current_table) > 1:  # At least 2 rows
                        tables.append({
                            "rows": current_table,
                            "columns": len(current_table[0].split('|')) if '|' in current_table[0] else len(current_table[0].split('\t'))
                        })
                    current_table = []
            
            return tables
            
        except Exception as e:
            return []
    
    async def extract_images(self, content: bytes, document_type: str) -> List[Dict[str, Any]]:
        """Extract images from document content"""
        try:
            # In production, you would extract images from PDFs, Word docs, etc.
            # For now, we'll create a mock implementation
            images = []
            
            if document_type == "application/pdf":
                # Mock PDF image extraction
                images.append({
                    "filename": "extracted_image_1.png",
                    "content": content[:1000],  # Mock image content
                    "format": "png"
                })
            
            return images
            
        except Exception as e:
            return []
    
    async def get_document_statistics(self, content: str) -> Dict[str, Any]:
        """Get statistics about the document"""
        try:
            words = content.split()
            sentences = content.split('.')
            paragraphs = content.split('\n\n')
            
            return {
                "word_count": len(words),
                "sentence_count": len(sentences),
                "paragraph_count": len(paragraphs),
                "character_count": len(content),
                "average_words_per_sentence": len(words) / len(sentences) if sentences else 0
            }
            
        except Exception as e:
            return {}
    
    async def validate_document(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Validate document and check for issues"""
        try:
            issues = []
            warnings = []
            
            # Check file size
            if len(content) > 50 * 1024 * 1024:  # 50MB
                issues.append("File size exceeds 50MB limit")
            
            # Check for empty content
            if len(content) == 0:
                issues.append("File is empty")
            
            # Check for binary content in text files
            if filename.endswith('.txt'):
                try:
                    content.decode('utf-8')
                except UnicodeDecodeError:
                    warnings.append("File contains binary content")
            
            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "warnings": warnings
            }
            
        except Exception as e:
            return {
                "valid": False,
                "issues": [f"Validation error: {str(e)}"],
                "warnings": []
            }
