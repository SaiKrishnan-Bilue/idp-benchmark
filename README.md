# Intelligent Document Parser — Benchmark Suite

> A reproducible benchmark evaluating cloud document intelligence services on text extraction, table detection, and key-value pair identification across a shared test corpus.

**Current status:** AWS Textract is live. Azure Document Intelligence and Google Document AI will be added once account setup is complete.

---

## Providers

| Provider | Service | Region | Status |
|----------|---------|--------|--------|
| **Amazon Web Services** | Textract (`AnalyzeDocument`) | Sydney (`ap-southeast-2`) | Live ✓ |
| **Microsoft Azure** | Document Intelligence (`prebuilt-layout`) | Australia East (`australiaeast`) | Coming soon |
| **Google Cloud** | Document AI (Form Parser) | US East (`us-east1`) | Coming soon |

> **Data residency note:** Google Document AI has no Australian region. It will be included for feature comparison only — documents are processed in the US.

---

## What Gets Measured

| Dimension | What is measured |
|-----------|-----------------|
| Text extraction | Character-level accuracy vs. manually verified ground truth |
| Table structure | Row/column detection rate, merged cell handling |
| Key-value pairs | Field identification and value accuracy |
| Latency | End-to-end API response time per page (median of 3 runs) |
| Cost per page | Based on published pricing at time of benchmark |

---

## Test Corpus

Five documents covering a range of document types and quality:

| File | Type |
|------|------|
| `berkshire-10k.png` | Financial report — dense text and tables |
| `declaration.jpg` | Historical document — old typography |
| `sears-1902.png` | Historical catalogue — multi-column layout |
| `vertical-ai-research-labs.png` | Modern document — clean layout, KV pairs |
| `wright-patent.png` | Patent — technical text |

---

## Prerequisites

**Python 3.12+**
```bash
python3.12 --version

# macOS: install via Homebrew if needed
brew install python@3.12
```

**AWS CLI**
```bash
brew install awscli
```

---

## Credentials

Store credentials in a `.env` file at the project root. This file is gitignored — never commit it.

```bash
cp .env.example .env
# Fill in your AWS keys
```

**AWS Textract** — found in: AWS Console → IAM → Users → your user → Security credentials → Access keys

```
AWS_ACCESS_KEY_ID=<your key ID>
AWS_SECRET_ACCESS_KEY=<your secret key>
AWS_DEFAULT_REGION=ap-southeast-2
```

Ensure your IAM user has `AmazonTextractFullAccess` attached.

---

## Project Structure

```
idp-benchmark/
├── .env                          # Credentials (gitignored)
├── .env.example                  # Template — safe to commit
├── .gitignore
├── README.md
├── requirements.txt
├── smoke_test.py                 # Quick end-to-end test
│
├── documents/
│   ├── test_corpus/              # Input documents
│   └── ground_truth/             # Expected results (JSON) — coming soon
│
└── src/
    └── providers/
        ├── base.py               # Abstract base class + result dataclasses
        └── aws.py                # AWS Textract client
```

---

## Setup

```bash
# Create virtual environment
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env with your AWS keys

# Verify AWS connection
set -a; source .env; set +a
python -m src.providers.aws --verify
```

---

## Running

**Smoke test — all documents through Textract:**
```bash
set -a; source .env; set +a
.venv/bin/python smoke_test.py
```

**Single document:**
```bash
.venv/bin/python smoke_test.py documents/test_corpus/berkshire-10k.png
```

---

## Result Schema

Each document run returns:

```json
{
  "provider": "aws",
  "document": "berkshire-10k.png",
  "pages": 1,
  "latency_ms": 1843,
  "raw_text": "...",
  "tables": [{ "row_count": 5, "column_count": 3, "rows": [...] }],
  "kv_pairs": [{ "key": "Date", "value": "2024-01-01", "confidence": 98.5 }]
}
```

---

## Pricing Reference

As of June 2026. Verify against current provider pricing pages before drawing cost conclusions.

| Provider | Feature | Free Tier | Pay-as-you-go |
|----------|---------|-----------|---------------|
| AWS Textract | AnalyzeDocument (TABLES + FORMS) | 1,000 pages/month (first 3 months) | ~$1.50 / 1,000 pages |
| Azure Document Intelligence | Layout (text + tables + KV) | 500 pages/month | ~$1.50 / 1,000 pages |
| Google Document AI | Form Parser | 1,000 pages/month | ~$1.50 / 1,000 pages |

---

## License

MIT
