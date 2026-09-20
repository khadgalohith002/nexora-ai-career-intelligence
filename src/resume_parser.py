from pypdf import PdfReader
from docx import Document
import io


def extract_text_from_pdf(uploaded_file):
    """Extract text from an uploaded PDF resume."""

    try:
        uploaded_file.seek(0)
        pdf_reader = PdfReader(uploaded_file)

        text = []

        for page in pdf_reader.pages:
            page_text = page.extract_text()

            if page_text:
                text.append(page_text)

        return "\n".join(text).strip()

    except Exception as e:
        return f"Error reading PDF: {str(e)}"


def extract_text_from_docx(uploaded_file):
    """Extract text from an uploaded DOCX resume."""

    try:
        uploaded_file.seek(0)

        file_bytes = uploaded_file.read()
        document = Document(io.BytesIO(file_bytes))

        text = []

        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text.strip())

        return "\n".join(text).strip()

    except Exception as e:
        return f"Error reading DOCX: {str(e)}"


def extract_resume_text(uploaded_file):
    """Detect the resume file type and extract its text."""

    if uploaded_file is None:
        return ""

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)

    elif file_name.endswith(".docx"):
        return extract_text_from_docx(uploaded_file)

    else:
        return "Error: Unsupported file format."
