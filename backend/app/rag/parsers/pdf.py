from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF

from backend.app.rag.parsers.base import ParsedDocument, ParsedPage


class PDFParser:
    async def parse(self, path: Path) -> ParsedDocument:
        return await self.parse_bytes(path.read_bytes(), path.name)

    async def parse_bytes(self, file_bytes: bytes, filename: str) -> ParsedDocument:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages: list[ParsedPage] = []

        for i, page in enumerate(doc, start=1):
            text = page.get_text("text")
            pages.append(ParsedPage(page_number=i, text=text, section_title=None))

        return ParsedDocument(pages=pages)
