import re
from collections import Counter
from dataclasses import dataclass
from io import BytesIO
from typing import Protocol

import PyPDF2
import streamlit as st

# ---------------- STOP WORDS ----------------
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


# ---------------- DATA STRUCTURE ----------------
@dataclass
class DocumentChunk:
    source: str
    page: int | None
    index: int
    text: str
    tokens: Counter[str]


class UploadedFileLike(Protocol):
    name: str

    def getvalue(self) -> bytes: ...


# ---------------- UI ----------------
def configure_page():  # pragma: no cover
    st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="wide")


# ---------------- TEXT CLEANING ----------------
def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9][a-zA-Z0-9_+-]*", text.lower())
    return [w for w in words if len(w) > 2 and w not in STOP_WORDS]


# ---------------- PDF EXTRACTION ----------------
def extract_pdf_pages(uploaded_file: UploadedFileLike):
    try:
        reader = PyPDF2.PdfReader(BytesIO(uploaded_file.getvalue()))
        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            raw_text = page.extract_text() or ""
            text = normalize_text(raw_text)

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

    except Exception as e:
        return [], f"Unable to process this PDF: {e}"


# ---------------- TEXT FILE ----------------
def extract_text_file(uploaded_file: UploadedFileLike):
    try:
        raw = uploaded_file.getvalue().decode("utf-8", errors="ignore")
        text = normalize_text(raw)
        if not text:
            return [], "The uploaded text file is empty."

        return [(None, text)], None
    except Exception as e:
        return [], f"Unable to process this text file: {e}"


# ---------------- CHUNKING ----------------
# ---------------- CHUNKING ----------------
def split_into_chunks(text: str, chunk_words: int, overlap_words: int):
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


def build_chunks(files, chunk_words, overlap_words):
    chunks: list[DocumentChunk] = []
    errors = []

    for file in files:
        if file.name.endswith(".pdf"):
            pages, error = extract_pdf_pages(file)
        else:
            pages, error = extract_text_file(file)

        if error:
            errors.append(f"{file.name}: {error}")
            continue

        for page_num, text in pages:
            for chunk in split_into_chunks(
                text,
                chunk_words,
                overlap_words,
            ):
                chunks.append(
                    DocumentChunk(
                        source=file.name,
                        page=page_num,
                        index=len(chunks) + 1,
                        text=chunk,
                        tokens=Counter(tokenize(chunk)),
                    )
                )

    return chunks, errors


# ---------------- RETRIEVAL ----------------
def score_chunk(query_tokens, chunk):
    overlap = set(query_tokens) & set(chunk.tokens)

    if not overlap:
        return 0

    return sum(chunk.tokens[token] for token in overlap)


def retrieve(query, chunks, top_k=3):
    query_tokens = tokenize(query)
    scored = [(c, score_chunk(query_tokens, c)) for c in chunks]
    scored = [(c, s) for c, s in scored if s > 0]
    scored.sort(key=lambda x: x[1], reverse=True)

    return scored[:top_k]


# ---------------- ANSWER GENERATION (FIXED) ----------------
def build_answer(query, matches):
    if not matches:
        return (
            "I could not find enough relevant information in the uploaded documents to answer that."
        )
    context = " ".join([chunk.text for chunk, _ in matches])
    q = query.lower()

    # -------- SKILLS --------
    if "skill" in q:
        skills_keywords = [
            "python",
            "sql",
            "html",
            "html5",
            "css",
            "java",
            "android",
            "sqlite",
            "xml",
            "javascript",
        ]

        found_skills = []

        for word in context.lower().split():
            word = word.strip(",.()[]{}")

            if word in skills_keywords and word not in found_skills:
                found_skills.append(word)

        if found_skills:
            return "Skills found in resume:\n- " + "\n- ".join(found_skills)

        return "No clear technical skills found."

    # -------- EDUCATION --------
    elif "education" in q:
        return "Education details:\n" + context[:1000]

    # -------- EXPERIENCE --------
    elif "experience" in q:
        return "Experience details:\n" + context[:1000]

    # -------- NAME --------
    elif "who" in q or "name" in q:
        return "Candidate info:\n" + context[:300]

    # -------- DEFAULT --------
    else:
        return context[:1200]


def source_label(chunk):
    if chunk.page is None:
        return f"{chunk.source}, chunk {chunk.index}"

    return f"{chunk.source}, page {chunk.page}, chunk {chunk.index}"


# ---------------- STREAMLIT APP ----------------
def main():  # pragma: no cover
    configure_page()

    uploaded_files = st.file_uploader(
        "Upload Resume PDF", type=["pdf", "txt"], accept_multiple_files=True
    )

    # rest of your code...
    if st.button("Build Index"):
        if uploaded_files:
            (
                st.session_state.chunks,
                st.session_state.errors,
            ) = build_chunks(
                uploaded_files,
                chunk_words=250,
                overlap_words=40,
            )

            st.success(f"Indexed {len(st.session_state.chunks)} chunks")
    chunks = st.session_state.get("chunks", [])

    if not chunks:
        st.info("Upload files and click Build Index")
        return

    query = st.chat_input("Ask something about resume")

    if query:
        matches = retrieve(query, chunks)
        answer = build_answer(query, matches)

        st.write("### Answer")
        st.write(answer)

        st.write("### Sources")
        for c, s in matches:
            st.write(f"{c.source} | score: {s}")
            st.write(c.text[:300])


if __name__ == "__main__":  # pragma: no cover
    main()
