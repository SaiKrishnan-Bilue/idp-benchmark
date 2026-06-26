import os
import sys
import time
from pathlib import Path

import boto3
from dotenv import load_dotenv

from .base import BaseProvider, KVPair, ProviderResult, Table

load_dotenv()


class TextractProvider(BaseProvider):
    name = "aws"

    def __init__(self):
        self.client = boto3.client(
            "textract",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION", "ap-southeast-2"),
        )

    def verify(self) -> bool:
        try:
            self.client.get_document_analysis(JobId="verify-check")
        except self.client.exceptions.InvalidJobIdException:
            return True  # reached Textract — credentials and region are valid
        except Exception:
            return False
        return True

    def analyze(self, document_path: str) -> ProviderResult:
        path = Path(document_path)
        with open(path, "rb") as f:
            doc_bytes = f.read()

        start = time.perf_counter()
        response = self.client.analyze_document(
            Document={"Bytes": doc_bytes},
            FeatureTypes=["TABLES", "FORMS"],
        )
        latency_ms = round((time.perf_counter() - start) * 1000, 2)

        blocks = response.get("Blocks", [])
        pages = response.get("DocumentMetadata", {}).get("Pages", 1)

        return ProviderResult(
            provider=self.name,
            document=path.name,
            pages=pages,
            latency_ms=latency_ms,
            raw_text=self._extract_text(blocks),
            tables=self._extract_tables(blocks),
            kv_pairs=self._extract_kv_pairs(blocks),
        )

    def _extract_text(self, blocks: list) -> str:
        return "\n".join(b["Text"] for b in blocks if b["BlockType"] == "LINE")

    def _extract_tables(self, blocks: list) -> list[Table]:
        block_map = {b["Id"]: b for b in blocks}
        tables = []

        for block in blocks:
            if block["BlockType"] != "TABLE":
                continue

            cells: dict[tuple[int, int], str] = {}
            for rel in block.get("Relationships", []):
                if rel["Type"] != "CHILD":
                    continue
                for cell_id in rel["Ids"]:
                    cell = block_map.get(cell_id)
                    if cell and cell["BlockType"] == "CELL":
                        coords = (cell["RowIndex"], cell["ColumnIndex"])
                        cells[coords] = self._get_cell_text(cell, block_map)

            if not cells:
                continue

            max_row = max(r for r, _ in cells)
            max_col = max(c for _, c in cells)
            rows = [
                [cells.get((r, c), "") for c in range(1, max_col + 1)]
                for r in range(1, max_row + 1)
            ]
            tables.append(Table(rows=rows, row_count=max_row, column_count=max_col))

        return tables

    def _get_cell_text(self, cell: dict, block_map: dict) -> str:
        words = []
        for rel in cell.get("Relationships", []):
            if rel["Type"] == "CHILD":
                for word_id in rel["Ids"]:
                    word = block_map.get(word_id)
                    if word and word["BlockType"] == "WORD":
                        words.append(word["Text"])
        return " ".join(words)

    def _extract_kv_pairs(self, blocks: list) -> list[KVPair]:
        block_map = {b["Id"]: b for b in blocks}
        kv_pairs = []

        for block in blocks:
            if block["BlockType"] != "KEY_VALUE_SET":
                continue
            if "KEY" not in block.get("EntityTypes", []):
                continue

            key_text = self._get_kv_text(block, block_map)
            confidence = round(block.get("Confidence", 0.0), 2)
            value_text = ""

            for rel in block.get("Relationships", []):
                if rel["Type"] == "VALUE":
                    for val_id in rel["Ids"]:
                        val_block = block_map.get(val_id)
                        if val_block:
                            value_text = self._get_kv_text(val_block, block_map)

            if key_text:
                kv_pairs.append(KVPair(key=key_text, value=value_text, confidence=confidence))

        return kv_pairs

    def _get_kv_text(self, block: dict, block_map: dict) -> str:
        words = []
        for rel in block.get("Relationships", []):
            if rel["Type"] == "CHILD":
                for word_id in rel["Ids"]:
                    word = block_map.get(word_id)
                    if not word:
                        continue
                    if word["BlockType"] == "SELECTION_ELEMENT":
                        words.append(word.get("SelectionStatus", ""))
                    elif word["BlockType"] == "WORD":
                        words.append(word.get("Text", ""))
        return " ".join(words)


if __name__ == "__main__":
    provider = TextractProvider()
    if "--verify" in sys.argv:
        ok = provider.verify()
        print(f"{'✓' if ok else '✗'} Textract — region: {provider.client.meta.region_name}")
        sys.exit(0 if ok else 1)
