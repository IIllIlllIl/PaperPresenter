from pathlib import Path

from src.lite.models import PaperMetadata, RenderedPage
from src.lite.pipeline import LitePipeline


class FakePDFReader:
    def read(self, pdf_path, output_dir):
        page_path = Path(output_dir) / "pages" / "page_001.png"
        page_path.parent.mkdir(parents=True, exist_ok=True)
        page_path.write_bytes(
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
            b"\x00\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe"
            b"\x02\xfeA\x83\xa3\x1d\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        return (
            PaperMetadata(title="Harness Paper", page_count=1, source_pdf=str(pdf_path)),
            "paper text",
            [RenderedPage(page_num=1, image_path=str(page_path), width=1, height=1, dpi=72)],
        )


class FakeWriter:
    def write(self, deck, output_path):
        Path(output_path).write_text("pptx placeholder", encoding="utf-8")


def test_lite_pipeline_writes_harness_manifest(tmp_path: Path):
    pdf_path = tmp_path / "paper.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")

    result = LitePipeline(pdf_reader=FakePDFReader(), writer=FakeWriter()).run(
        pdf_path,
        output_dir=tmp_path / "out",
    )

    manifest = Path(result["manifest"])
    assert manifest.exists()
    assert Path(result["plan"]).exists()
    assert Path(result["pptx"]).exists()
    assert "FullPageFallbackInventory" in manifest.read_text(encoding="utf-8")
