import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from app.tools.notes_generator.core import executor

# Pleae run the test from the root directory of the project 
# PYTHONPATH=./ pytest app/tools/notes_generator/tests/test_core.py

base_attributes = {
    "focus_topic": "Plant Growth",
    "lang": "en"
}

@pytest.fixture
def mock_chain_and_loader(mocker):
    """
    1) Mocks `get_docs` to return a real Document (with empty metadata dict).
    2) Mocks `load_summarize_chain` so it doesn't instantiate a real LLM,
       returning a fake chain that yields "Mocked Summary".
    """
    # (A) Mock the doc loader to return a real Document with an empty metadata dict
    mock_get_docs = mocker.patch(
        "app.tools.notes_generator.core.get_docs",
        return_value=[Document(page_content="Mocked Document Content", metadata={})]
    )

    # (B) Mock the summarize chain so no real LLM is created
    mock_load_chain = mocker.patch(
        "app.tools.notes_generator.tools.load_summarize_chain"
    )
    fake_chain = MagicMock()
    fake_chain.run.return_value = "Mocked Summary"
    mock_load_chain.return_value = fake_chain

    # Mock the ChatGoogleGenerativeAI so .invoke(...) returns "Mocked Summary"
    mock_llm_class = mocker.patch("app.tools.notes_generator.tools.ChatGoogleGenerativeAI")
    mock_llm_instance = MagicMock()
    mock_llm_instance.invoke.return_value = "Mocked Summary"
    mock_llm_class.return_value = mock_llm_instance

    #return mock_get_docs, mock_load_chain, fake_chain, mock_llm_class
    return mock_load_chain, mock_llm_class



def test_executor_text_content_valid(mock_chain_and_loader):
    """Provide text_content only, no doc_url/doc_type."""
    result = executor(
        **base_attributes,
        text_content="Some sample text about plants and photosynthesis."
    )
    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert "notes" in result
    assert "Mocked Summary" in result["notes"]


def test_executor_missing_all_inputs(mock_chain_and_loader):
    """Expect error if doc_url/doc_type/text_content all missing."""
    result = executor(**base_attributes)
    assert result["status"] == "error"
    assert "Either 'doc_url' or 'text_content' must be provided." in result["message"]


def test_executor_pdf_doc_url_valid(mock_chain_and_loader):
    """doc_url w/ PDF, doc_type='pdf' => success, 'Mocked Summary' in notes."""
    result = executor(
        **base_attributes,
        doc_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
        doc_type="pdf"
    )
    assert result["status"] == "success"
    assert "notes" in result
    assert "Mocked Summary" in result["notes"]


def test_executor_pdf_doc_url_invalid(mock_chain_and_loader):
    result = executor(
            **base_attributes,
            doc_url="https://filesamples.com/samples/document/pdf/sample1.pdf",
            doc_type=1
        )
    assert result["status"] == "error"
    assert "Unsupported doc_type" in result["message"]


def test_executor_csv_doc_url_valid(mock_chain_and_loader):
    result = executor(
        **base_attributes,
        doc_url="https://filesamples.com/samples/document/csv/sample1.csv",
        doc_type="csv"
    )
    assert result["status"] == "success"
    assert "notes" in result
    assert "Mocked Summary" in result["notes"]


def test_executor_csv_doc_url_invalid(mock_chain_and_loader):
    result = executor(
            **base_attributes,
            doc_url="https://filesamples.com/samples/document/csv/sample1.csv",
            doc_type=1
        )
    assert result["status"] == "error"
    assert "Unsupported doc_type" in result["message"]

def test_executor_txt_doc_url_valid(mock_chain_and_loader):
    result = executor(
        **base_attributes,
        doc_url="https://filesamples.com/samples/document/txt/sample1.txt",
        doc_type="txt"
    )
    assert result["status"] == "success"
    assert "notes" in result
    assert "Mocked Summary" in result["notes"]


def test_executor_txt_doc_url_invalid(mock_chain_and_loader):
    result = executor(
            **base_attributes,
            doc_url="https://filesamples.com/samples/document/txt/sample1.txt",
            doc_type=1
        )
    assert result["status"] == "error"
    assert "Unsupported doc_type" in result["message"]

def test_executor_md_doc_url_valid(mock_chain_and_loader):
    result = executor(
        **base_attributes,
        doc_url="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
        doc_type="md"
    )
    assert result["status"] == "success"
    assert "notes" in result
    assert "Mocked Summary" in result["notes"]


def test_executor_md_doc_url_invalid(mock_chain_and_loader):
    result = executor(
            **base_attributes,
            doc_url="https://github.com/radicalxdev/kai-ai-backend/blob/main/README.md",
            doc_type=1
        )
    assert result["status"] == "error"
    assert "Unsupported doc_type" in result["message"]

def test_executor_pptx_doc_url_valid(mock_chain_and_loader):
    result = executor(
        **base_attributes,
        doc_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
        doc_type="pptx"
    )
    assert result["status"] == "success"
    assert "notes" in result
    assert "Mocked Summary" in result["notes"]


def test_executor_pptx_doc_url_invalid(mock_chain_and_loader):
    result = executor(
            **base_attributes,
            doc_url="https://scholar.harvard.edu/files/torman_personal/files/samplepptx.pptx",
            doc_type=1
        )
    assert result["status"] == "error"
    assert "Unsupported doc_type" in result["message"]

def test_executor_docx_doc_url_valid(mock_chain_and_loader):
    result = executor(
        **base_attributes,
        doc_url="https://filesamples.com/samples/document/docx/sample1.docx",
        doc_type="docx"
    )
    assert result["status"] == "success"
    assert "notes" in result
    assert "Mocked Summary" in result["notes"]


def test_executor_docx_doc_url_invalid(mock_chain_and_loader):
    result = executor(
            **base_attributes,
            doc_url="https://filesamples.com/samples/document/docx/sample1.docx",
            doc_type=1
        )
    assert result["status"] == "error"
    assert "Unsupported doc_type" in result["message"]

def test_executor_xls_doc_url_valid(mock_chain_and_loader):
    result = executor(
        **base_attributes,
        doc_url="https://filesamples.com/samples/document/xls/sample1.xls",
        doc_type="xls"
    )
    assert result["status"] == "success"
    assert "notes" in result
    assert "Mocked Summary" in result["notes"]


def test_executor_xls_doc_url_invalid(mock_chain_and_loader):
    result = executor(
            **base_attributes,
            doc_url="https://filesamples.com/samples/document/xls/sample1.xls",
            doc_type=1
        )
    assert result["status"] == "error"
    assert "Unsupported doc_type" in result["message"]

def test_executor_xlsx_doc_url_valid(mock_chain_and_loader):
    result = executor(
        **base_attributes,
        doc_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
        doc_type="xlsx"
    )
    assert result["status"] == "success"
    assert "notes" in result
    assert "Mocked Summary" in result["notes"]


def test_executor_xlsx_doc_url_invalid(mock_chain_and_loader):
    result = executor(
            **base_attributes,
            doc_url="https://filesamples.com/samples/document/xlsx/sample1.xlsx",
            doc_type=1
        )
    assert result["status"] == "error"
    assert "Unsupported doc_type" in result["message"]

def test_executor_gpdf_doc_url_valid(mock_chain_and_loader):
    result = executor(
        **base_attributes,
        doc_url="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
        doc_type="gpdf"
    )
    assert result["status"] == "success"
    assert "notes" in result
    assert "Mocked Summary" in result["notes"]


def test_executor_gpdf_doc_url_invalid(mock_chain_and_loader):
    result = executor(
            **base_attributes,
            doc_url="https://drive.google.com/file/d/1fUj1uWIMh6QZsPkt0Vs7mEd2VEqz3O8l/view",
            doc_type=1
        )
    assert result["status"] == "error"
    assert "Unsupported doc_type" in result["message"]