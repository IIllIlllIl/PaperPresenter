"""PDF ingestion and page rendering for PaperPresenter Lite."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import fitz
from PIL import Image

from src.lite.models import PaperMetadata, RenderedPage


class LitePDFReader:
    """Read metadata, text, and rendered pages from one PDF."""

    def __init__(self, dpi: int = 160):
        self.dpi = dpi

    def read(self, pdf_path: str | Path, output_dir: str | Path) -> Tuple[PaperMetadata, str, List[RenderedPage]]:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(f"Expected a PDF file: {pdf_path}")

        output_dir = Path(output_dir)
        page_dir = output_dir / "pages"
        page_dir.mkdir(parents=True, exist_ok=True)

        doc = fitz.open(str(pdf_path))
        try:
            metadata = self._metadata(doc, pdf_path)
            text = "\n\n".join(page.get_text("text") for page in doc)
            pages = self._render_pages(doc, page_dir)
            return metadata, text, pages
        finally:
            doc.close()

    def _metadata(self, doc: fitz.Document, pdf_path: Path) -> PaperMetadata:
        raw = doc.metadata or {}
        title = (raw.get("title") or "").strip() or pdf_path.stem
        author_text = (raw.get("author") or "").strip()
        authors = [part.strip() for part in author_text.replace(";", ",").split(",") if part.strip()]
        return PaperMetadata(
            title=title,
            authors=authors,
            page_count=len(doc),
            source_pdf=str(pdf_path),
        )

    def _render_pages(self, doc: fitz.Document, page_dir: Path) -> List[RenderedPage]:
        zoom = self.dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        rendered: List[RenderedPage] = []

        for index, page in enumerate(doc, start=1):
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            path = page_dir / f"page_{index:03d}.png"
            pixmap.save(str(path))
            with Image.open(path) as image:
                width, height = image.size
            rendered.append(
                RenderedPage(
                    page_num=index,
                    image_path=str(path),
                    width=width,
                    height=height,
                    dpi=self.dpi,
                )
            )

        return rendered

