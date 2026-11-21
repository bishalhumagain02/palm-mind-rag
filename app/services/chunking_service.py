from collections.abc import Sequence

def fixed_size_chunking(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be positive and overlap must be in [0, chunk_size)")
    chunks: list[str] = []
    step = chunk_size - overlap
    for start in range(0, len(text), step):
        chunk = text[start:start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        if start + chunk_size >= len(text):
            break
    return chunks

def recursive_chunking(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
    """Split preferentially at paragraph, line, sentence, then word boundaries."""
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be positive and overlap must be in [0, chunk_size)")
    separators: Sequence[str] = ("\n\n", "\n", ". ", " ")
    def split_long(piece: str, level: int = 0) -> list[str]:
        if len(piece) <= chunk_size:
            return [piece]
        if level >= len(separators):
            step = chunk_size - overlap
            return [piece[i:i + chunk_size] for i in range(0, len(piece), step)]
        sep = separators[level]
        parts = piece.split(sep)
        if len(parts) == 1:
            return split_long(piece, level + 1)
        out: list[str] = []
        for part in parts:
            if part:
                out.extend(split_long(part, level + 1) if len(part) > chunk_size else [part])
        return out
    pieces = split_long(text)
    chunks: list[str] = []
    current = ""
    for piece in pieces:
        piece = piece.strip()
        if not piece:
            continue
        candidate = f"{current} {piece}".strip()
        if len(candidate) <= chunk_size:
            current = candidate
            continue
        if current:
            chunks.append(current)
        carry = current[-overlap:] if overlap and current else ""
        current = f"{carry} {piece}".strip()
        if len(current) > chunk_size:
            current = current[-chunk_size:]
    if current:
        chunks.append(current)
    return chunks

def chunk_text(text: str, strategy: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
    if strategy == "fixed_size":
        return fixed_size_chunking(text, chunk_size, overlap)
    if strategy == "recursive":
        return recursive_chunking(text, chunk_size, overlap)
    raise ValueError("Unknown chunking strategy")
