from PyPDF2 import PdfReader
from io import BytesIO
from typing import Optional

class PDFProcessor:
    def extract_text(self, file_contents: bytes) -> Optional[str]:
        try:
            reader = PdfReader(BytesIO(file_contents))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"PDF processing error: {e}")
            return None