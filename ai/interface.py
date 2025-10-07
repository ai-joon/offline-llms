import os
import base64
from pathlib import Path
from typing import List

import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

from loader import load_index, get_or_create_pdf_index


def _inject_dark_mode(enabled: bool) -> None:
    if not enabled:
        return
    st.markdown(
        """
        <style>
        html, body, [data-testid="stAppViewContainer"] { background-color: #0e1117 !important; color: #e6edf3 !important; }
        .stButton > button { background-color: #21262d !important; border-color: #30363d !important; color: #e6edf3 !important; white-space: nowrap !important; min-width: 100px; padding: 0.5rem 1rem; text-align: center; height: 40px !important; }
        /* Consistent number input width (e.g., pagination) */
        [data-testid="stNumberInput"] input { width: 90px !important; text-align: center !important; height: 40px !important; }
        [data-testid="stNumberInput"] { margin: 0 6px !important; }
        /* Tidy spacing for inline controls */
        .stButton > button { margin: 0 6px !important; }
        .stTextInput, .stTextArea, .stSelectbox, .stNumberInput, .stSlider, .stFileUploader, .stRadio { color: #e6edf3 !important; }
        .stMarkdown, .stMarkdown p { color: #e6edf3 !important; }
        .stChatMessage { background-color: #161b22 !important; }
        /* Header & chat input */
        [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stMainMenu"] { background-color: #0d1117 !important; color: #e6edf3 !important; border-bottom: 1px solid #30363d !important; }
        [data-testid="stMainMenu"] * { color: #e6edf3 !important; }
        [data-testid="stChatInput"] { background-color: #0d1117 !important; border-top: 1px solid #30363d !important; }
        [data-testid="stChatInput"] textarea, [data-testid="stChatInput"] input { background-color: #161b22 !important; color: #e6edf3 !important; border: 1px solid #30363d !important; }
        [data-testid="stChatInput"] textarea::placeholder, [data-testid="stChatInput"] input::placeholder { color: #8b949e !important; }
        [data-testid="stChatInput"] button { background-color: #21262d !important; border: 1px solid #30363d !important; color: #e6edf3 !important; }
        /* Chat input uses Streamlit default placement (after chat content) */
        /* Sidebar */
        [data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #30363d !important; }
        [data-testid="stSidebar"] * { color: #e6edf3 !important; }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4, [data-testid="stSidebar"] h5, [data-testid="stSidebar"] h6 { color: #e6edf3 !important; }
        [data-testid="stSidebar"] .stButton > button { background-color: #21262d !important; border-color: #30363d !important; color: #e6edf3 !important; }
        [data-testid="stSidebar"] input, [data-testid="stSidebar"] textarea, [data-testid="stSidebar"] select { background-color: #161b22 !important; color: #e6edf3 !important; border: 1px solid #30363d !important; }
        [data-testid="stSidebar"] .stTextInput > div > div,
        [data-testid="stSidebar"] .stNumberInput > div > div,
        [data-testid="stSidebar"] .stSelectbox > div,
        [data-testid="stSidebar"] .stTextArea > div > textarea,
        [data-testid="stSidebar"] .stFileUploader > div { background-color: #161b22 !important; border: 1px solid #30363d !important; }
        [data-testid="stSidebar"] .stSlider [role="slider"] { background-color: #238636 !important; border: 1px solid #2ea043 !important; }
        [data-testid="stSidebar"] .stSlider .st-bx { background-color: #30363d !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _ensure_state() -> None:
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("db", None)
    st.session_state.setdefault("top_k", 4)
    st.session_state.setdefault("retrieval_mode", "similarity")
    st.session_state.setdefault("max_tokens", 256)
    st.session_state.setdefault("max_context_chars", 4000)
    st.session_state.setdefault("last_sources", [])
    st.session_state.setdefault("_is_generating", False)
    st.session_state.setdefault("_pending_msg", None)
    st.session_state.setdefault("selected_pdf", None)
    st.session_state.setdefault("current_pdf_index", None)


def _display_pdf(pdf_path: str, height: int = 600) -> None:
    try:
        if not os.path.exists(pdf_path):
            st.caption(f"PDF not found: {pdf_path}")
            return

        # Try high-compatibility image rendering (PyMuPDF)
        try:
            import fitz  # type: ignore

            doc = fitz.open(pdf_path)
            total_pages = doc.page_count or 1
            safe_key = pdf_path.replace("\\", "_").replace("/", "_")
            page_key = f"pdf_page_{safe_key}"
            curr_page = int(st.session_state.get(page_key, 1))

            # Render current page at a sensible zoom for clarity
            page = doc.load_page(max(0, min(int(total_pages) - 1, curr_page - 1)))
            zoom = 2.0
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            st.image(pix.tobytes("png"), caption=f"Page {curr_page}/{total_pages}", use_container_width=True)

            # Centered pagination controls (horizontal with even margins)
            cL, cPrev, cPage, cNext, cR = st.columns([4, 1, 1.4, 1, 4])
            with cPrev:
                st.markdown("<div style='display:flex;align-items:center;justify-content:center;height:40px;'>", unsafe_allow_html=True)
                if st.button("◀ Prev", key=f"prev_{safe_key}"):
                    st.session_state[page_key] = max(1, curr_page - 1)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with cPage:
                st.markdown("<div style='display:flex;align-items:center;justify-content:center;height:40px;'>", unsafe_allow_html=True)
                page_num = int(
                    st.number_input(
                        " ",
                        min_value=1,
                        max_value=int(total_pages),
                        value=curr_page,
                        step=1,
                        key=f"num_{safe_key}",
                        label_visibility="collapsed",
                    )
                )
                if page_num != curr_page:
                    st.session_state[page_key] = page_num
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with cNext:
                st.markdown("<div style='display:flex;align-items:center;justify-content:center;height:40px;'>", unsafe_allow_html=True)
                if st.button("Next ▶", key=f"next_{safe_key}"):
                    st.session_state[page_key] = min(int(total_pages), curr_page + 1)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            return
        except Exception:
            pass

        # Fallback: embed with data URI and download option
        with open(pdf_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode("utf-8")
        file_name = os.path.basename(pdf_path) or "document.pdf"
        html = f"""
        <div style='width:100%; border: 1px solid #30363d;'>
          <object data="data:application/pdf;base64,{b64}" type="application/pdf" width="100%" height="{height}">
            <embed src="data:application/pdf;base64,{b64}" type="application/pdf" width="100%" height="{height}" />
            <p>PDF preview not supported. <a href="data:application/pdf;base64,{b64}" download="{file_name}">Download</a></p>
          </object>
        </div>
        """
        st.components.v1.html(html, height=height + 20)
        st.download_button("Download PDF", data=data, file_name=file_name, mime="application/pdf")
    except Exception as e:
        st.caption(f"Unable to display PDF: {e}")


def _answer(query: str, top_k: int, llm_model: str, base_url: str, show_ctx: bool, retrieval_mode: str, max_context_chars: int, max_tokens: int):
    db = st.session_state.get("db")
    if db is None:
        # If no index is loaded, answer using general knowledge
        template = (
            "You are a helpful assistant. Answer the question using your general knowledge.\n"
            "Be informative and helpful in your response.\n\n"
            "Question: {question}\nAnswer:"
        )
        prompt = PromptTemplate.from_template(template).format(question=query)
    else:
        if retrieval_mode == "mmr":
            retriever = db.as_retriever(search_type="mmr", search_kwargs={"k": top_k, "fetch_k": max(10, top_k * 5)})
        else:
            retriever = db.as_retriever(search_kwargs={"k": top_k})
        ctx_docs = retriever.invoke(query)
        
        # Trim context to a character budget to speed up generation
        parts: List[str] = []
        total = 0
        for d in ctx_docs:
            text = d.page_content or ""
            remaining = max_context_chars - total
            if remaining <= 0:
                break
            if len(text) > remaining:
                text = text[:remaining]
            if text:
                parts.append(text)
                total += len(text)
        context = "\n\n".join(parts)
        # Sanitize to avoid surrogate/invalid unicode issues on Windows terminals or downstream libs
        context = context.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")

        # Check if context is empty or very short (likely irrelevant)
        if not context.strip() or len(context.strip()) < 50:
            # Use general knowledge template when no relevant context is found
            template = (
                "You are a helpful assistant. Answer the question using your general knowledge.\n"
                "Be informative and helpful in your response.\n\n"
                "Question: {question}\nAnswer:"
            )
            prompt = PromptTemplate.from_template(template).format(question=query)
            ctx_docs = []  # No context to show
        else:
            # Use context-aware template when relevant context is available
            template = (
                "You are a helpful assistant. Answer the question using the provided context when available and relevant.\n"
                "If the context doesn't contain the answer, use your general knowledge to provide a helpful response.\n"
                "Always be helpful and informative, whether using context or general knowledge.\n\n"
                "Question: {question}\nContext:\n{context}\nAnswer:"
            )
            prompt = PromptTemplate.from_template(template).format(question=query, context=context)

    llm = OllamaLLM(model=llm_model, base_url=base_url, temperature=0.2, num_predict=max_tokens)

    placeholder = st.empty()
    streamed = ""
    for token in llm.stream(prompt):
        streamed += token
        placeholder.markdown(streamed)

    if show_ctx and ctx_docs:
        with st.expander("Show retrieved context"):
            for i, d in enumerate(ctx_docs, start=1):
                st.markdown(f"**Chunk {i}**")
                st.write(d.page_content[:1200] + ("..." if len(d.page_content) > 1200 else ""))
                if d.metadata:
                    st.caption(str(d.metadata))
                st.markdown("---")
    elif show_ctx and not ctx_docs:
        with st.expander("Show retrieved context"):
            st.info("No relevant context found. Answer based on general knowledge.")

    return streamed, ctx_docs


def main() -> None:
    _ensure_state()

    st.set_page_config(page_title="AI Chatbot", page_icon="💬", layout="wide")
    st.title("💬 AI Chatbot")

    with st.sidebar:
        st.header("Settings")
        dark = st.toggle("Dark mode", value=True)
        _inject_dark_mode(dark)

        # Defaults from environment or sensible fallbacks
        index_dir = Path(os.environ.get("FAISS_INDEX_DIR", str(Path.cwd() / "faiss_index")))
        emb_model = os.environ.get("OLLAMA_EMBED", "nomic-embed-text")
        base_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        # llm_model = os.environ.get("OLLAMA_LLM", "qwen2.5:0.5b-instruct")
        llm_model = os.environ.get("OLLAMA_LLM", "qwen2.5:3b-instruct")


        # Display current index status
        if st.session_state.get("current_pdf_index"):
            st.success(f"📄 Active: {os.path.basename(st.session_state['current_pdf_index'])}")
        elif st.session_state.get("db") is not None:
            st.info(f"📚 Using global index")
        else:
            st.warning("⚠️ No document selected - answers will be based on general knowledge only")
        
        st.markdown("---")
        st.session_state["top_k"] = st.slider("Top-k context", min_value=1, max_value=10, value=st.session_state["top_k"]) 
        st.session_state["retrieval_mode"] = st.radio("Retrieval", options=["similarity", "mmr"], index=(0 if st.session_state["retrieval_mode"] == "similarity" else 1))
        st.session_state["max_context_chars"] = st.number_input("Max context size (chars)", min_value=500, max_value=20000, value=st.session_state["max_context_chars"], step=500)
        st.session_state["max_tokens"] = st.slider("Max answer tokens", min_value=32, max_value=2048, value=st.session_state["max_tokens"], step=32)

        cols = st.columns(1)
        with cols[0]:
            if st.button("Clear chat"):
                st.session_state["messages"] = []

    col_left, col_right = st.columns([2, 1])

    with col_left:
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"]) 

        is_generating = st.session_state.get("_is_generating", False)
        user_msg = st.chat_input("Ask me anything…", disabled=is_generating)
        if user_msg and not is_generating:
            st.session_state["messages"].append({"role": "user", "content": user_msg})
            with st.chat_message("user"):
                st.markdown(user_msg)

            with st.chat_message("assistant"):
                st.session_state["_is_generating"] = True
                show_ctx = st.toggle("Show context", value=False, key=f"show_ctx_{len(st.session_state['messages'])}")
                answer, sources = _answer(
                    user_msg,
                    st.session_state["top_k"],
                    llm_model,
                    base_url,
                    show_ctx,
                    st.session_state["retrieval_mode"],
                    int(st.session_state["max_context_chars"]),
                    int(st.session_state["max_tokens"]),
                )
            st.session_state["messages"].append({"role": "assistant", "content": answer})
            st.session_state["last_sources"] = sources
            st.session_state["_is_generating"] = False

    with col_right:
        # st.subheader("Sources")
        sources = st.session_state.get("last_sources", [])
        if not sources:
            print("No sources")
        else:
            # Group pages by source file
            from collections import defaultdict
            src_pages = defaultdict(set)
            for d in sources:
                src = d.metadata.get("source") or d.metadata.get("file_path") or "<unknown>"
                page = d.metadata.get("page")
                if isinstance(page, int):
                    src_pages[src].add(page)
                else:
                    src_pages[src]

            for src, pages in src_pages.items():
                name = os.path.basename(str(src))
                st.markdown(f"**{name}**")
                st.caption(f"{src}  |  pages: {', '.join(str(p) for p in sorted(pages)) if pages else 'n/a'}")
                st.markdown("---")

        st.subheader("📚 Document Selection")
        default_pdf = r"C:\Source\research\docx\report-ko.pdf"
        # File selector: list PDFs in default directory plus manual entry
        import glob
        default_dir = os.path.dirname(default_pdf)
        options = []
        if os.path.isdir(default_dir):
            options = sorted(glob.glob(os.path.join(default_dir, "*.pdf")))
        
        # Get unique options (remove duplicates)
        all_options = list(dict.fromkeys([default_pdf] + options))
        
        # Find the index of previously selected PDF or use default
        default_index = 0
        if st.session_state.get("selected_pdf") and st.session_state["selected_pdf"] in all_options:
            default_index = all_options.index(st.session_state["selected_pdf"])
        
        selected = st.selectbox("Choose a PDF", options=all_options, index=default_index, key="pdf_selector")
        
        # Check if PDF selection has changed
        if selected != st.session_state.get("selected_pdf"):
            st.session_state["selected_pdf"] = selected
            # Load or create index for the selected PDF
            indices_base_dir = Path.cwd() / "faiss_indices"
            with st.spinner(f"Loading/creating index for {os.path.basename(selected)}..."):
                try:
                    st.session_state["db"] = get_or_create_pdf_index(
                        selected, 
                        indices_base_dir,
                        emb_model=emb_model,
                        base_url=base_url
                    )
                    st.session_state["current_pdf_index"] = selected
                    st.success(f"Index ready for {os.path.basename(selected)}")
                    # Clear messages when switching documents
                    st.session_state["messages"] = []
                    st.session_state["last_sources"] = []
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading/creating index: {e}")
                    st.session_state["db"] = None
        
        _display_pdf(selected, height=700)


if __name__ == "__main__":
    main()


