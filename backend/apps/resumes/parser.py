"""Resume parser using pdfplumber with fallback."""
import logging
import io

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file) -> str:
    """Extract text from an uploaded PDF file-like object."""
    try:
        import pdfplumber
        if hasattr(file, "read"):
            data = file.read()
        else:
            data = file
        text_parts = []
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
        return "\n".join(text_parts).strip()
    except Exception as e:
        logger.warning("pdfplumber failed (%s), trying PyPDF2", e)
        try:
            from PyPDF2 import PdfReader
            if hasattr(file, "read"):
                data = file.read()
            else:
                data = file
            reader = PdfReader(io.BytesIO(data))
            return "\n".join((p.extract_text() or "") for p in reader.pages).strip()
        except Exception as e2:
            logger.error("PDF extraction failed: %s", e2)
            return ""