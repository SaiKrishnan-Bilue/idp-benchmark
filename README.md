# Intelligent Document Parser — Benchmark Suite

> A reproducible, head-to-head benchmark comparing **Azure Document Intelligence**, **AWS Textract**, and **Google Document AI** on text extraction, table detection, and key-value pair identification across a shared test corpus.

---

## What This Benchmarks

Three cloud document intelligence services are run against the same set of test documents and measured across a consistent set of dimensions:

| Dimension | What is measured |
|-----------|-----------------|
| Text extraction accuracy | Character-level accuracy vs. manually verified ground truth |
| Table structure detection | Row/column detection rate, merged cell handling |
| Key-value pair extraction | Field identification and value accuracy |
| Latency | End-to-end API response time per page (median of 3 runs) |
| Cost per page | Based on published pricing at time of benchmark |

---

## Providers

| Provider | Service | Region | Free Tier |
|----------|---------|--------|-----------|
| **Microsoft Azure** | Document Intelligence (`prebuilt-layout`) | Australia East (`australiaeast`) | 500 pages/month |
| **Amazon Web Services** | Textract (`AnalyzeDocument`) | Sydney (`ap-southeast-2`) | 1,000 pages/month (first 3 months) |
| **Google Cloud** | Document AI (Form Parser) | US East (`us-east1`) | 1,000 pages/month |

> **Data residency note:** Google Document AI has no Australian region. It is included for feature comparison only. Documents sent to Google are processed in the US. Do not use for data subject to Australian data residency requirements.

---

## Prerequisites

### Python

Python **3.12+** is required.

```bash
python3.12 --version
# Python 3.12.x

# macOS: install via Homebrew if needed
brew install python@3.12
```

### Cloud CLIs

Optional but strongly recommended for initial account setup and credential verification:

```bash
brew install azure-cli             # az
brew install awscli                # aws
brew install --cask google-cloud-sdk  # gcloud
```

---

## Credentials You Will Need

Before running any benchmarks, collect the following from each provider's console. Store them in a `.env` file (see Setup below — this file is gitignored and must never be committed).

### Azure Document Intelligence

Found in: **Azure Portal → your Document Intelligence resource → Keys and Endpoint**

```
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://<resource-name>.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=<Key 1 or Key 2>
```

### AWS Textract

Found in: **AWS Console → IAM → Users → your user → Security credentials → Access keys**

```
AWS_ACCESS_KEY_ID=<your key ID>
AWS_SECRET_ACCESS_KEY=<your secret key>
AWS_DEFAULT_REGION=ap-southeast-2
```

Ensure your IAM user or role has the `AmazonTextractFullAccess` policy attached (or a scoped policy permitting `textract:AnalyzeDocument`).

### Google Document AI

Found in: **GCP Console → IAM & Admin → Service Accounts → your service account → Keys**

```
GOOGLE_APPLICATION_CREDENTIALS=./credentials/gcp-service-account.json
GCP_PROJECT_ID=<your-project-id>
GCP_PROCESSOR_ID=<your-processor-id>
GCP_LOCATION=us
```

Place your downloaded service account JSON file at `credentials/gcp-service-account.json`. This path is gitignored.

---

## Project Structure

```
idp-benchmark/
├── .env                              # All credentials (gitignored)
├── .env.example                      # Template — commit this, not .env
├── .gitignore
├── README.md
├── requirements.txt
│
├── credentials/
│   └── gcp-service-account.json      # GCP service account key (gitignored)
│
├── documents/
│   ├── test_corpus/                  # Input PDFs for benchmarking
│   └── ground_truth/                 # Expected extraction results (JSON)
│
├── src/
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py                   # Abstract base class all providers implement
│   │   ├── azure.py                  # Azure Document Intelligence client
│   │   ├── aws.py                    # AWS Textract client
│   │   └── gcp.py                    # Google Document AI client
│   │
│   ├── benchmark/
│   │   ├── __init__.py
│   │   ├── runner.py                 # Orchestrates runs across providers/documents
│   │   ├── metrics.py                # Accuracy, latency, and cost calculations
│   │   └── report.py                 # Generates comparison output (JSON + HTML)
│   │
│   └── utils/
│       ├── __init__.py
│       └── document.py               # Shared document loading and normalisation
│
├── tests/
│   ├── test_azure.py
│   ├── test_aws.py
│   └── test_gcp.py
│
└── results/
    └── .gitkeep                      # Benchmark output lands here (gitignored)
```

---

## Setup

### 1. Create a virtual environment

```bash
cd idp-benchmark
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
# Open .env and fill in your values for each provider
```

### 3. Verify connections

Once credentials are in place, verify each provider before running benchmarks:

```bash
python -m src.providers.azure --verify
python -m src.providers.aws --verify
python -m src.providers.gcp --verify
```

Each command sends a minimal test request and prints the service version or a confirmation response.

---

## Running Benchmarks

### Run all providers against the full test corpus

```bash
python -m src.benchmark.runner --all
```

### Run a single provider

```bash
python -m src.benchmark.runner --provider azure
python -m src.benchmark.runner --provider aws
python -m src.benchmark.runner --provider gcp
```

### Run against a single document

```bash
python -m src.benchmark.runner --provider azure --doc documents/test_corpus/invoice_sample.pdf
```

### Generate a comparison report

```bash
python -m src.benchmark.report --input results/latest/ --format html
```

---

## Understanding Results

Each benchmark run writes output to a timestamped directory under `results/`:

```
results/
└── 20260626_143000/
    ├── azure_results.json
    ├── aws_results.json
    ├── gcp_results.json
    └── comparison_report.html
```

Each result file follows this schema:

```json
{
  "provider": "azure",
  "document": "invoice_sample.pdf",
  "pages": 2,
  "latency_ms": 1843,
  "text_accuracy": 0.987,
  "tables_detected": 3,
  "table_structure_accuracy": 0.941,
  "kv_pairs_extracted": 12,
  "kv_accuracy": 0.917,
  "cost_usd": 0.003
}
```

---

## Pricing Reference

As of June 2026. Always verify against current provider pricing pages before drawing cost conclusions.

| Provider | Feature | Free Tier | Pay-as-you-go |
|----------|---------|-----------|---------------|
| Azure Document Intelligence | Layout (text + tables + KV) | 500 pages/month | ~$1.50 / 1,000 pages |
| AWS Textract | AnalyzeDocument (TABLES + FORMS) | 1,000 pages/month (3 months) | ~$1.50 / 1,000 pages |
| Google Document AI | Form Parser | 1,000 pages/month | ~$1.50 / 1,000 pages |

> AWS Textract pricing note: `AnalyzeDocument` (tables + forms) costs more than `DetectDocumentText` (text only). This benchmark uses `AnalyzeDocument` to enable a fair feature comparison.

---

## Limitations

- **Google data residency:** No Australian region. Documents are processed in `us-east1`. Factor this into any compliance assessment.
- **Ground truth dependency:** Accuracy scores are relative to this project's manually verified test corpus. Results will differ across document types and quality.
- **Latency variability:** Measured values depend on document size, provider load, and network conditions. Median of 3 runs is reported per document.
- **Free tier exhaustion:** If you exceed the free tier during benchmarking, charges will apply to your account. Monitor usage in each provider's console.
- **Model versions:** Cloud providers update their underlying models. Results should be tagged with the API version used (captured automatically in result JSON).

---

## License

MIT
