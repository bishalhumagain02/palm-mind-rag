import pytest
from app.services.chunking_service import fixed_size_chunking, recursive_chunking, chunk_text

def test_fixed_chunks_overlap():
    chunks = fixed_size_chunking("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 10, 2)
    assert chunks[0] == "ABCDEFGHIJ"
    assert chunks[1].startswith("IJ")
    assert chunks[-1].endswith("Z") and len(chunks[-1]) == 10

def test_fixed_invalid_args():
    with pytest.raises(ValueError):
        fixed_size_chunking("hello", 5, 5)

def test_recursive_chunks_bounded():
    text = "Paragraph one has a few words.\n\nParagraph two has several more words.\n\nParagraph three ends here."
    chunks = recursive_chunking(text, 35, 5)
    assert chunks
    assert all(len(chunk) <= 35 for chunk in chunks)

def test_selector():
    assert chunk_text("hello", "fixed_size", 10, 2) == ["hello"]
