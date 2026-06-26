"""
Quick smoke test — runs every file in documents/test_corpus/ through Textract
and prints a summary of what was extracted.

Usage:
    python smoke_test.py
    python smoke_test.py documents/test_corpus/berkshire-10k.png  # single file
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

from src.providers.aws import TextractProvider

load_dotenv()

CORPUS = Path("documents/test_corpus")
SUPPORTED = {".pdf", ".png", ".jpg", ".jpeg", ".tiff"}


def run(path: Path, provider: TextractProvider) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {path.name}")
    print(f"{'─' * 60}")

    result = provider.analyze(str(path))

    print(f"  Pages        : {result.pages}")
    print(f"  Latency      : {result.latency_ms:.0f} ms")
    print(f"  Text lines   : {len(result.raw_text.splitlines())}")
    print(f"  Tables found : {len(result.tables)}")
    print(f"  KV pairs     : {len(result.kv_pairs)}")

    if result.tables:
        t = result.tables[0]
        print(f"\n  First table ({t.row_count} rows × {t.column_count} cols):")
        for row in t.rows[:3]:
            print(f"    {row}")
        if t.row_count > 3:
            print(f"    … {t.row_count - 3} more rows")

    if result.kv_pairs:
        print(f"\n  First 5 key-value pairs:")
        for kv in result.kv_pairs[:5]:
            print(f"    [{kv.confidence:.0f}%]  {kv.key!r:30s} → {kv.value!r}")

    print(f"\n  Text preview:")
    for line in result.raw_text.splitlines()[:5]:
        print(f"    {line}")


def main() -> None:
    provider = TextractProvider()
    print("Textract Smoke Test")
    print(f"Region: {provider.client.meta.region_name}\n")

    if len(sys.argv) > 1:
        files = [Path(sys.argv[1])]
    else:
        files = sorted(f for f in CORPUS.iterdir() if f.suffix.lower() in SUPPORTED)

    if not files:
        print(f"No supported files found in {CORPUS}")
        sys.exit(1)

    for path in files:
        try:
            run(path, provider)
        except Exception as e:
            print(f"\n  ERROR on {path.name}: {e}")

    print(f"\n{'─' * 60}")
    print(f"Done — {len(files)} file(s) processed.")


if __name__ == "__main__":
    main()
