from __future__ import annotations

from pathlib import Path

from backend.app.rag.parsers.base import ParsedDocument, ParsedPage


class TXTParser:
    async def parse(self, path: Path) -> ParsedDocument:
        return await self.parse_bytes(path.read_bytes(), path.name)

    async def parse_bytes(self, file_bytes: bytes, filename: str) -> ParsedDocument:
        text = file_bytes.decode("utf-8")
        page = ParsedPage(page_number=1, text=text, section_title=None)
        return ParsedDocument(pages=[page])
