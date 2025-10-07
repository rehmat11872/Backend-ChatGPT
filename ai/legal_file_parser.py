import io

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from docx import Document
except ImportError:
    Document = None

class LegalFileParser:
    def __init__(self):
        self.max_files = 5
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        self.max_pdf_pages = 20
        self.max_tokens = 3000
        
    def count_tokens(self, text):
        return len(text) // 4  # Approximate
    
    def validate_file(self, file):
        if file.size > self.max_file_size:
            return {"error": f"File {file.name} exceeds 5MB limit"}
        
        if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]:
            return {"error": f"Unsupported file format: {file.name}. Only PDF, DOCX, TXT allowed"}
        
        return {"valid": True}
    
    def parse_pdf(self, file):
        if not PyPDF2:
            return {"error": "PDF processing not available. Install PyPDF2."}
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            
            if len(pdf_reader.pages) > self.max_pdf_pages:
                return {"error": f"PDF {file.name} has {len(pdf_reader.pages)} pages. Maximum 20 pages allowed"}
            
            text_content = ""
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text.strip():
                    text_content += f"[Page {page_num}]\n{page_text}\n\n"
            
            return {"content": text_content, "filename": file.name}
            
        except Exception as e:
            return {"error": f"Failed to parse PDF {file.name}: {str(e)}"}
    
    def parse_docx(self, file):
        if not Document:
            return {"error": "DOCX processing not available. Install python-docx."}
        try:
            doc = Document(io.BytesIO(file.read()))
            
            text_content = ""
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content += paragraph.text + "\n"
            
            return {"content": text_content, "filename": file.name}
            
        except Exception as e:
            return {"error": f"Failed to parse DOCX {file.name}: {str(e)}"}
    
    def parse_txt(self, file):
        try:
            text_content = file.read().decode('utf-8')
            return {"content": text_content, "filename": file.name}
            
        except Exception as e:
            return {"error": f"Failed to parse TXT {file.name}: {str(e)}"}
    
    def parse_files(self, files):
        if len(files) > self.max_files:
            return {"error": f"Maximum {self.max_files} files allowed per chat"}
        
        parsed_files = []
        total_content = ""
        
        for file in files:
            validation = self.validate_file(file)
            if "error" in validation:
                return validation
            
            if file.content_type == "application/pdf":
                result = self.parse_pdf(file)
            elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                result = self.parse_docx(file)
            elif file.content_type == "text/plain":
                result = self.parse_txt(file)
            else:
                return {"error": f"Unsupported file type: {file.content_type}"}
            
            if "error" in result:
                return result
            
            parsed_files.append(result)
            total_content += f"\n--- {result['filename']} ---\n{result['content']}\n"
        
        if self.count_tokens(total_content) > self.max_tokens:
            total_content = total_content[:self.max_tokens * 4] + "\n\n[Content truncated due to length]"
        
        return {
            "success": True,
            "combined_content": total_content,
            "files_processed": len(parsed_files)
        }