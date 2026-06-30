from pathlib import Path

import fitz
from PIL import Image

from src.lite.pdf_render import LitePDFReader


def _make_pdf(path: Path, title: str = "Fixture Paper") -> None:
    doc = fitz.open()
    page = doc.new_page(width=240, height=320)
    page.insert_text((36, 72), "Fixture paper text for intake and rendering.")
    doc.set_metadata({"title": title, "author": "Ada Lovelace; Alan Turing"})
    doc.save(path)
    doc.close()


def test_lite_pdf_reader_extracts_metadata_and_text(tmp_path: Path):
    pdf_path = tmp_path / "fixture paper.pdf"
    _make_pdf(pdf_path)

    metadata, text, pages = LitePDFReader(dpi=72).read(pdf_path, tmp_path / "out")

    assert metadata.title == "Fixture Paper"
    assert metadata.authors == ["Ada Lovelace", "Alan Turing"]
    assert metadata.page_count == 1
    assert "Fixture paper text" in text
    assert len(pages) == 1


def test_lite_pdf_reader_renders_page_png(tmp_path: Path):
    pdf_path = tmp_path / "fixture paper.pdf"
    _make_pdf(pdf_path)

    _, _, pages = LitePDFReader(dpi=72).read(pdf_path, tmp_path / "out")
    rendered = Path(pages[0].image_path)

    assert rendered.exists()
    assert rendered.name == "page_001.png"
    with Image.open(rendered) as image:
        assert image.width > 0
        assert image.height > 0
    assert pages[0].width > 0
    assert pages[0].height > 0


def test_lite_pdf_reader_rejects_non_pdf(tmp_path: Path):
    text_path = tmp_path / "paper.txt"
    text_path.write_text("not a pdf", encoding="utf-8")

    try:
        LitePDFReader().read(text_path, tmp_path / "out")
    except ValueError as exc:
        assert "Expected a PDF" in str(exc)
    else:
        raise AssertionError("Expected non-PDF path to raise ValueError")

