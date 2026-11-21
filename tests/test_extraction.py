import pytest
from app.services.document_extraction import extract_document_text, clean_text

def test_txt_extraction():
    assert extract_document_text(b"hello", "sample.txt") == "hello"

def test_unsupported_extension():
    with pytest.raises(ValueError):
        extract_document_text(b"x", "file.docx")

def test_clean_text():
    assert clean_text("a\r\n\n\n b\t c") == "a\n\n b c"
