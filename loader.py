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