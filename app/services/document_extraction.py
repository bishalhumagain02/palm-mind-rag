from pathlib import Path
import re
import pymupdf

def extract_text_from_txt(content: bytes) -> str:
    return content.decode("utf-8-sig")

def extract_text_from_pdf(content: bytes) -> str:
    with pymupdf.open(stream=content, filetype="pdf") as pdf:
        return "\n\n".join(page.get_text() for page in pdf)

def extract_document_text(content: bytes, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".txt":
        return extract_text_from_txt(content)
    if suffix == ".pdf":
        return extract_text_from_pdf(content)
    raise ValueError("Only PDF and TXT files are supported")

def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")
    text = re.sub(r"[ ]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
