from collections import Counter
from dataclasses import dataclass
from io import BytesIO

import PyPDF2

from app import (
    DocumentChunk,
    build_answer,
    build_chunks,
    extract_pdf_pages,
    extract_text_file,
    normalize_text,
    retrieve,
    score_chunk,
    source_label,
    split_into_chunks,
    tokenize,
)


@dataclass
class FakeUpload:
    name: str
    content: bytes

    def getvalue(self) -> bytes:
        return self.content


@dataclass
class BrokenUpload:
    name: str

    def getvalue(self) -> bytes:
        raise ValueError("cannot read upload")


def test_normalize_text_collapses_whitespace() -> None:
    assert normalize_text("  Hello\n\nworld\tfrom   RAG  ") == "Hello world from RAG"


def test_tokenize_filters_stop_words_and_short_words() -> None:
    assert tokenize("The RAG chatbot is built for PDF and TXT files.") == [
        "rag",
        "chatbot",
        "built",
        "pdf",
        "txt",
        "files",
    ]


def test_split_into_chunks_uses_overlap() -> None:
    chunks = split_into_chunks("one two three four five six", chunk_words=3, overlap_words=1)

    assert chunks == ["one two three", "three four five", "five six"]


def test_extract_text_file_returns_normalized_text() -> None:
    pages, error = extract_text_file(FakeUpload("notes.txt", b"First line.\nSecond line."))

    assert error is None
    assert pages == [(None, "First line. Second line.")]


def test_extract_text_file_rejects_empty_upload() -> None:
    pages, error = extract_text_file(FakeUpload("empty.txt", b" \n\t "))

    assert pages == []
    assert error == "The uploaded text file is empty."


def test_extract_pdf_pages_reports_invalid_pdf() -> None:
    pages, error = extract_pdf_pages(FakeUpload("broken.pdf", b"not a pdf"))

    assert pages == []
    assert error == "This PDF could not be read. Please upload a valid, unencrypted PDF."


def test_extract_pdf_pages_reports_pdf_without_text() -> None:
    pdf_buffer = BytesIO()
    writer = PyPDF2.PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.write(pdf_buffer)

    pages, error = extract_pdf_pages(FakeUpload("blank.pdf", pdf_buffer.getvalue()))

    assert pages == []
    assert (
        error
        == "No readable text was found. Scanned PDFs need OCR before this chatbot can read them."
    )


def test_extract_file_helpers_report_unexpected_read_errors() -> None:
    assert extract_text_file(BrokenUpload("notes.txt")) == (
        [],
        "Unable to process this text file: cannot read upload",
    )
    assert extract_pdf_pages(BrokenUpload("notes.pdf")) == (
        [],
        "Unable to process this PDF: cannot read upload",
    )


def test_build_chunks_indexes_text_uploads() -> None:
    chunks, errors = build_chunks(
        [FakeUpload("notes.md", b"Streamlit builds local data apps for documents.")],
        chunk_words=5,
        overlap_words=1,
    )

    assert errors == []
    assert len(chunks) == 2
    assert chunks[0].source == "notes.md"
    assert chunks[0].page is None
    assert chunks[0].index == 1


def test_build_chunks_collects_file_errors() -> None:
    chunks, errors = build_chunks([FakeUpload("empty.txt", b"")], chunk_words=5, overlap_words=1)

    assert chunks == []
    assert errors == ["empty.txt: The uploaded text file is empty."]


def test_split_into_chunks_handles_empty_text() -> None:
    assert split_into_chunks("", chunk_words=5, overlap_words=1) == []


def test_retrieve_returns_best_matching_chunk_first() -> None:
    chunks = build_sample_chunks()

    matches = retrieve("How does retrieval find sources?", chunks, top_k=2)

    assert matches[0][0].source == "retrieval.txt"
    assert matches[0][1] > 0


def test_score_chunk_returns_zero_without_overlap() -> None:
    chunk = DocumentChunk(
        source="notes.txt",
        page=None,
        index=1,
        text="Streamlit runs locally.",
        tokens=tokenize_counter("streamlit runs locally"),
    )

    assert score_chunk(tokenize_counter("unrelated topic"), chunk) == 0


def test_score_chunk_returns_zero_without_tokens() -> None:
    chunk = DocumentChunk(source="notes.txt", page=None, index=1, text="", tokens=Counter())

    assert score_chunk(Counter(), chunk) == 0


def test_build_answer_uses_relevant_sentences() -> None:
    chunks = build_sample_chunks()
    matches = retrieve("What does the chatbot cite?", chunks, top_k=2)

    answer = build_answer("What does the chatbot cite?", matches)

    assert "source passages" in answer


def test_build_answer_handles_no_matches() -> None:
    assert build_answer("unknown topic", []) == (
        "I could not find enough relevant information in the uploaded documents to answer that."
    )


def test_build_answer_falls_back_to_chunk_preview() -> None:
    chunk = DocumentChunk(
        source="notes.txt",
        page=None,
        index=1,
        text="No matching sentence terms are present.",
        tokens=tokenize_counter("matching sentence terms"),
    )

    assert build_answer("unrelated", [(chunk, 0.1)]) == chunk.text


def test_source_label_omits_page_for_text_files() -> None:
    chunk = DocumentChunk(
        source="guide.txt",
        page=None,
        index=3,
        text="A useful passage.",
        tokens=tokenize_counter("useful passage"),
    )

    assert source_label(chunk) == "guide.txt, chunk 3"


def test_source_label_includes_page_when_present() -> None:
    chunk = DocumentChunk(
        source="guide.pdf",
        page=4,
        index=9,
        text="A useful passage.",
        tokens=tokenize_counter("useful passage"),
    )

    assert source_label(chunk) == "guide.pdf, page 4, chunk 9"


def tokenize_counter(text: str) -> Counter[str]:
    return Counter(tokenize(text))


def build_sample_chunks() -> list[DocumentChunk]:
    uploads = [
        FakeUpload(
            "retrieval.txt",
            b"Retrieval finds relevant chunks from documents. The chatbot cites source passages.",
        ),
        FakeUpload("setup.txt", b"Streamlit runs the local web application."),
    ]
    chunks, errors = build_chunks(uploads, chunk_words=20, overlap_words=0)
    assert errors == []
    return chunks
