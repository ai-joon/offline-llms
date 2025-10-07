from pathlib import Path
from typing import List, Sequence, Union, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS


def load_pdfs(paths: Sequence[Union[str, Path]]) -> List[Document]:
    documents: List[Document] = []
    for p in paths:
        loader = PyPDFLoader(str(p))
        documents.extend(loader.load())
    return documents


def split_documents(documents: List[Document], chunk_size: int = 250, chunk_overlap: int = 50) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(documents)


def _sanitize_text(text: str) -> str:
    # Remove invalid surrogate code points and any undecodable bytes
    return (text or "").encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")


def _sanitize_documents(documents: List[Document]) -> List[Document]:
    cleaned: List[Document] = []
    for d in documents:
        txt = _sanitize_text(d.page_content)
        if txt.strip():
            cleaned.append(Document(page_content=txt, metadata=d.metadata))
    return cleaned


def build_index_from_docs(documents: List[Document], emb_model: str = "nomic-embed-text", base_url: str = "http://localhost:11434") -> FAISS:
    chunks = split_documents(documents)
    chunks = _sanitize_documents(chunks)
    embeddings = OllamaEmbeddings(model=emb_model, base_url=base_url)
    return FAISS.from_documents(chunks, embeddings)


def build_index_from_pdf_paths(paths: Sequence[Union[str, Path]], emb_model: str = "nomic-embed-text", base_url: str = "http://localhost:11434") -> FAISS:
    documents = load_pdfs(paths)
    return build_index_from_docs(documents, emb_model=emb_model, base_url=base_url)


def save_index(db: FAISS, out_dir: Union[str, Path]) -> Path:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    db.save_local(str(out_path))
    return out_path


def load_index(index_dir: Union[str, Path], emb_model: str = "nomic-embed-text", base_url: str = "http://localhost:11434") -> FAISS:
    embeddings = OllamaEmbeddings(model=emb_model, base_url=base_url)
    # allow_dangerous_deserialization is needed for pickle-based docstore
    return FAISS.load_local(str(index_dir), embeddings, allow_dangerous_deserialization=True)


def get_pdf_index_name(pdf_path: Union[str, Path]) -> str:
    """Generate a unique index directory name for a PDF file."""
    import hashlib
    pdf_path = Path(pdf_path)
    # Use filename without extension as base
    base_name = pdf_path.stem
    # Add hash of full path to ensure uniqueness
    path_hash = hashlib.md5(str(pdf_path.absolute()).encode()).hexdigest()[:8]
    return f"faiss_index_{base_name}_{path_hash}"


def get_or_create_pdf_index(
    pdf_path: Union[str, Path],
    indices_dir: Union[str, Path],
    emb_model: str = "nomic-embed-text",
    base_url: str = "http://localhost:11434",
) -> FAISS:
    """
    Load existing index for a PDF or create a new one if it doesn't exist.
    
    Args:
        pdf_path: Path to the PDF file
        indices_dir: Directory to store all indices
        emb_model: Ollama embedding model name
        base_url: Ollama base URL
    
    Returns:
        FAISS vector store for the PDF
    """
    pdf_path = Path(pdf_path)
    indices_dir = Path(indices_dir)
    indices_dir.mkdir(parents=True, exist_ok=True)
    
    # Get the specific index directory for this PDF
    index_name = get_pdf_index_name(pdf_path)
    index_path = indices_dir / index_name
    
    # Check if index already exists
    if index_path.exists() and (index_path / "index.faiss").exists():
        # Load existing index
        return load_index(index_path, emb_model=emb_model, base_url=base_url)
    else:
        # Create new index from PDF
        db = build_index_from_pdf_paths([pdf_path], emb_model=emb_model, base_url=base_url)
        save_index(db, index_path)
        return db


def build_and_save_index_from_pdf_paths(
    paths: Sequence[Union[str, Path]],
    out_dir: Union[str, Path],
    emb_model: str = "nomic-embed-text",
    base_url: str = "http://localhost:11434",
) -> Path:
    db = build_index_from_pdf_paths(paths, emb_model=emb_model, base_url=base_url)
    return save_index(db, out_dir)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build and persist FAISS index from PDFs using Ollama embeddings.")
    parser.add_argument("--pdf", action="append", help="Path to a PDF file (can be specified multiple times)")
    parser.add_argument("--dir", type=str, help="Directory to scan for PDFs (glob *.pdf)", default="")
    parser.add_argument("--out", type=str, help="Output directory for FAISS index", default="faiss_index")
    parser.add_argument("--emb", type=str, help="Embedding model tag (Ollama)", default="nomic-embed-text")
    parser.add_argument("--base", type=str, help="Ollama base URL", default="http://localhost:11434")

    args = parser.parse_args()

    pdfs: List[Path] = []
    if args.pdf:
        pdfs.extend([Path(p) for p in args.pdf])
    if args.dir:
        d = Path(args.dir)
        if d.exists():
            pdfs.extend(sorted(d.glob("*.pdf")))

    if not pdfs:
        raise SystemExit("No PDFs provided. Use --pdf path or --dir directory.")

    out_path = build_and_save_index_from_pdf_paths(pdfs, args.out, emb_model=args.emb, base_url=args.base)
    print(f"Saved FAISS index to {out_path}")