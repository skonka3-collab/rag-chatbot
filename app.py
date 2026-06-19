import math
import re
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from html import escape
from io import BytesIO
from typing import Protocol

import PyPDF2
import streamlit as st

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "were",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


@dataclass
class DocumentChunk:
    source: str
    page: int | None
    index: int
    text: str
    tokens: Counter[str]


class UploadedFileLike(Protocol):
    name: str

    def getvalue(self) -> bytes:
        """Return the uploaded file content as bytes."""


def configure_page() -> None:
    st.set_page_config(page_title="RAG Chatbot", page_icon="Chat", layout="wide")
    st.markdown(
        """
        <style>
            .main .block-container {max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem;}
            .hero {
                border: 1px solid #dbe4ef; border-radius: 8px; padding: 1.35rem 1.5rem;
                background: linear-gradient(135deg, #f8fafc 0%, #eef6ff 58%, #f7fee7 100%);
                margin-bottom: 1rem;
            }
            .hero h1 {margin: 0 0 .35rem 0; color: #0f172a; letter-spacing: 0;}
            .hero p {margin: 0; color: #475569;}
            div[data-testid="stMetric"] {
                border: 1px solid #dbe4ef; border-radius: 8px; padding: .75rem .95rem;
                background: #f8fafc;
            }
            .source-box {
                border: 1px solid #dbe4ef; border-radius: 8px; padding: .85rem 1rem;
                background: #ffffff; margin-bottom: .75rem;
            }
            .source-title {font-weight: 700; color: #0f172a; margin-bottom: .35rem;}
            .source-text {color: #334155; font-size: .95rem; line-height: 1.45;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9][a-zA-Z0-9_+-]*", text.lower())
    return [word for word in words if len(word) > 2 and word not in STOP_WORDS]


def extract_pdf_pages(
    uploaded_file: UploadedFileLike,
) -> tuple[list[tuple[int | None, str]], str | None]:
    try:
        reader = PyPDF2.PdfReader(BytesIO(uploaded_file.getvalue()))
        pages: list[tuple[int | None, str]] = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = normalize_text(page.extract_text() or "")
            if text:
                pages.append((page_number, text))
        if not pages:
            return (
                [],
                "No readable text was found. Scanned PDFs need OCR before this chatbot can read them.",
            )
        return pages, None
    except PyPDF2.errors.PdfReadError:
        return [], "This PDF could not be read. Please upload a valid, unencrypted PDF."
    except Exception as exc:
        return [], f"Unable to process this PDF: {exc}"


def extract_text_file(
    uploaded_file: UploadedFileLike,
) -> tuple[list[tuple[int | None, str]], str | None]:
    try:
        raw_text = uploaded_file.getvalue().decode("utf-8", errors="ignore")
        text = normalize_text(raw_text)
        if not text:
            return [], "The uploaded text file is empty."
        return [(None, text)], None
    except Exception as exc:
        return [], f"Unable to process this text file: {exc}"


def split_into_chunks(text: str, chunk_words: int, overlap_words: int) -> list[str]:
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    step = max(chunk_words - overlap_words, 1)
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + chunk_words]).strip()
        if chunk:
            chunks.append(chunk)
        if start + chunk_words >= len(words):
            break
    return chunks


def build_chunks(
    uploaded_files: Sequence[UploadedFileLike],
    chunk_words: int,
    overlap_words: int,
) -> tuple[list[DocumentChunk], list[str]]:
    chunks: list[DocumentChunk] = []
    errors: list[str] = []

    for uploaded_file in uploaded_files:
        name = uploaded_file.name
        pages: list[tuple[int | None, str]]
        if name.lower().endswith(".pdf"):
            pages, error = extract_pdf_pages(uploaded_file)
        else:
            pages, error = extract_text_file(uploaded_file)

        if error:
            errors.append(f"{name}: {error}")
            continue

        for page_number, page_text in pages:
            for chunk_text in split_into_chunks(page_text, chunk_words, overlap_words):
                chunks.append(
                    DocumentChunk(
                        source=name,
                        page=page_number,
                        index=len(chunks) + 1,
                        text=chunk_text,
                        tokens=Counter(tokenize(chunk_text)),
                    )
                )

    return chunks, errors


def score_chunk(query_tokens: Counter[str], chunk: DocumentChunk) -> float:
    if not query_tokens or not chunk.tokens:
        return 0.0

    overlap = set(query_tokens) & set(chunk.tokens)
    if not overlap:
        return 0.0

    score = 0.0
    for token in overlap:
        score += (1 + math.log(query_tokens[token])) * (1 + math.log(chunk.tokens[token]))
    length_penalty = math.sqrt(sum(value * value for value in chunk.tokens.values()))
    return score / max(length_penalty, 1.0)


def retrieve(
    query: str, chunks: list[DocumentChunk], top_k: int
) -> list[tuple[DocumentChunk, float]]:
    query_tokens = Counter(tokenize(query))
    ranked = [(chunk, score_chunk(query_tokens, chunk)) for chunk in chunks]
    ranked = [(chunk, score) for chunk, score in ranked if score > 0]
    ranked.sort(key=lambda item: item[1], reverse=True)
    return ranked[:top_k]


def build_answer(query: str, matches: list[tuple[DocumentChunk, float]]) -> str:
    if not matches:
        return (
            "I could not find enough relevant information in the uploaded documents to answer that."
        )

    query_terms = set(tokenize(query))
    selected_sentences = []

    for chunk, _score in matches:
        sentences = re.split(r"(?<=[.!?])\s+", chunk.text)
        scored_sentences = []
        for sentence in sentences:
            sentence_terms = set(tokenize(sentence))
            overlap = len(query_terms & sentence_terms)
            if overlap:
                scored_sentences.append((overlap, sentence.strip()))

        scored_sentences.sort(key=lambda item: item[0], reverse=True)
        for _overlap, sentence in scored_sentences[:2]:
            if sentence and sentence not in selected_sentences:
                selected_sentences.append(sentence)
            if len(selected_sentences) >= 5:
                break
        if len(selected_sentences) >= 5:
            break

    if not selected_sentences:
        selected_sentences = [matches[0][0].text[:700]]

    answer = " ".join(selected_sentences)
    return answer[:1400] + ("..." if len(answer) > 1400 else "")


def source_label(chunk: DocumentChunk) -> str:
    if chunk.page is None:
        return f"{chunk.source}, chunk {chunk.index}"
    return f"{chunk.source}, page {chunk.page}, chunk {chunk.index}"


def render_sources(matches: list[tuple[DocumentChunk, float]]) -> None:
    if not matches:
        return

    st.subheader("Retrieved Sources")
    for chunk, score in matches:
        label = escape(source_label(chunk))
        preview_text = chunk.text[:650] + ("..." if len(chunk.text) > 650 else "")
        preview = escape(preview_text)
        st.markdown(
            f"""
            <div class="source-box">
                <div class="source-title">{label} | relevance {score:.2f}</div>
                <div class="source-text">{preview}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def initialize_state() -> None:
    st.session_state.setdefault("chunks", [])
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("document_names", [])


def main() -> None:
    configure_page()
    initialize_state()

    st.markdown(
        """
        <div class="hero">
            <h1>RAG Chatbot</h1>
            <p>Upload documents, ask questions, and get answers grounded in the retrieved source passages.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Knowledge Base")
        uploaded_files = st.file_uploader(
            "Upload PDF or TXT files",
            type=["pdf", "txt", "md"],
            accept_multiple_files=True,
        )
        chunk_words = st.slider("Chunk size", min_value=120, max_value=500, value=260, step=20)
        overlap_words = st.slider("Chunk overlap", min_value=0, max_value=120, value=45, step=5)
        top_k = st.slider("Sources per answer", min_value=1, max_value=6, value=3)

        if st.button("Build / Refresh Index", type="primary", use_container_width=True):
            if uploaded_files:
                with st.spinner("Reading documents and building retrieval index..."):
                    chunks, errors = build_chunks(uploaded_files, chunk_words, overlap_words)
                st.session_state.chunks = chunks
                st.session_state.document_names = [file.name for file in uploaded_files]
                st.session_state.messages = []
                if errors:
                    for error in errors:
                        st.warning(error)
                st.success(
                    f"Indexed {len(chunks)} chunks from {len(st.session_state.document_names)} file(s)."
                )
            else:
                st.warning("Upload at least one document first.")

        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []

    chunks = st.session_state.chunks
    document_names = st.session_state.document_names

    cols = st.columns(3)
    cols[0].metric("Documents", len(document_names))
    cols[1].metric("Chunks", len(chunks))
    cols[2].metric("Messages", len(st.session_state.messages))

    if not chunks:
        st.info("Upload documents in the sidebar, then click Build / Refresh Index.")
        return

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    query = st.chat_input("Ask a question about the uploaded documents")
    if not query:
        return

    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    matches = retrieve(query, chunks, top_k)
    answer = build_answer(query, matches)
    cited_answer = answer
    if matches:
        citations = ", ".join(
            f"[{index}] {source_label(chunk)}"
            for index, (chunk, _score) in enumerate(matches, start=1)
        )
        cited_answer = f"{answer}\n\nSources: {citations}"

    st.session_state.messages.append({"role": "assistant", "content": cited_answer})
    with st.chat_message("assistant"):
        st.markdown(cited_answer)

    render_sources(matches)


if __name__ == "__main__":
    main()
