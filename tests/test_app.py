from dataclasses import dataclass

from app import (
    DocumentChunk,
    build_answer,
    build_chunks,
    extract_text_file,
    normalize_text,
    retrieve,
    split_into_chunks,
    tokenize,
)


@dataclass
class FakeUpload:
    name: str
    content: bytes

    def getvalue(self) -> bytes:
        return self.content


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


def test_retrieve_returns_best_matching_chunk_first() -> None:
    chunks = build_sample_chunks()

    matches = retrieve("How does retrieval find sources?", chunks, top_k=2)

    assert matches[0][0].source == "retrieval.txt"
    assert matches[0][1] > 0


def test_build_answer_uses_relevant_sentences() -> None:
    chunks = build_sample_chunks()
    matches = retrieve("What does the chatbot cite?", chunks, top_k=2)

    answer = build_answer("What does the chatbot cite?", matches)

    assert "source passages" in answer


def test_build_answer_handles_no_matches() -> None:
    assert build_answer("unknown topic", []) == (
        "I could not find enough relevant information in the uploaded documents to answer that."
    )


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
