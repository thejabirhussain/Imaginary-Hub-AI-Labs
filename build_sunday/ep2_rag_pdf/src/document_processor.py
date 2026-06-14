import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any
from src.utils import clean_text, time_it

class DocumentProcessor:
    """
    Handles loading, parsing, and text extraction from single or multiple PDF files.
    
    EDUCATIONAL INSIGHT: Why PyMuPDF (fitz) over PyPDF2?
    - PyMuPDF is a wrapper around MuPDF, a lightweight and highly optimized PDF/document engine written in C.
    - Speed: PyMuPDF is up to 10-100x faster than pure Python parsers like PyPDF2.
    - Layout analysis: It parses document structure, columns, and character coordinates much more accurately.
    - Rich metadata: PyMuPDF handles fonts, links, image extractions, and complex structures out of the box.
    """

    def __init__(self, uploads_dir: Path):
        self.uploads_dir = Path(uploads_dir)
        # Ensure the uploads directory exists
        self.uploads_dir.mkdir(parents=True, exist_ok=True)

    @time_it
    def load_pdf(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Parses a single PDF file and extracts text page-by-page.
        
        Returns:
            A list of dictionaries containing:
            - "text": Cleaned extracted string of page text
            - "metadata": Dict with document name, page number, total pages, etc.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"PDF document not found at: {file_path}")
            
        print(f"📄 Processing: {file_path.name}")
        pages_data = []
        
        try:
            # Open PDF document via PyMuPDF
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            for page_idx in range(total_pages):
                page = doc.load_page(page_idx)
                # Extract text using structural/blocks layout to handle double columns nicely
                raw_text = page.get_text("text")
                cleaned = clean_text(raw_text)
                
                # Check for scanned pages/empty text
                if not cleaned:
                    # In production, this would trigger OCR (e.g. Tesseract)
                    cleaned = "[Image or Unextractable Text]"
                
                metadata = {
                    "document_name": file_path.name,
                    "document_path": str(file_path.absolute()),
                    "page_number": page_idx,
                    "total_pages": total_pages,
                    "char_count": len(cleaned),
                    "word_count": len(cleaned.split())
                }
                
                pages_data.append({
                    "text": cleaned,
                    "metadata": metadata
                })
            
            doc.close()
            print(f"✅ Extracted {total_pages} pages from '{file_path.name}'.")
            
        except Exception as e:
            print(f"❌ Error parsing {file_path.name}: {str(e)}")
            raise e
            
        return pages_data

    @time_it
    def load_all_pdfs(self) -> List[Dict[str, Any]]:
        """
        Scans the uploads directory and processes all present PDF files.
        """
        all_pages = []
        pdf_files = list(self.uploads_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"⚠️ No PDF documents found in uploads directory: {self.uploads_dir}")
            return []
            
        print(f"📂 Found {len(pdf_files)} PDF(s) in {self.uploads_dir.name}")
        for pdf_path in pdf_files:
            try:
                pages_data = self.load_pdf(pdf_path)
                all_pages.extend(pages_data)
            except Exception as e:
                print(f"⚠️ Skipping '{pdf_path.name}' due to error.")
                
        return all_pages

# Self-test when executing document_processor directly
if __name__ == "__main__":
    from src.config import Config
    processor = DocumentProcessor(Config.UPLOADS_DIR)
    results = processor.load_all_pdfs()
    if results:
        print(f"Parsed {len(results)} total pages.")
        print(f"First page sample metadata: {results[0]['metadata']}")
