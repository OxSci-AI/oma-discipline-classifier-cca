# oma-discipline-classifier-cca

OMA Discipline Classifier Cca Service

## Quick Start

### 1. Configure AWS CodeArtifact

```bash
./entrypoint-dev.sh
```

### 2. Install Dependencies

```bash
poetry install
```

### 3. Run Discipline Classifier Test

```bash
poetry run python tests/test_agents.py --test classifier
```

### 4. Run Service

```bash
poetry run uvicorn app.core.main:app --reload --port 8080
```

Access the API documentation at: http://localhost:8080/docs

## Architecture

### Discipline Classification Pipeline

- **Phase 1: Paper Parsing** - Extract structure, terms, discipline hints from PDF or structured content
- **Phase 2: Discipline Classification** - ID-based classification (1-23 academic disciplines)

### 23 Academic Disciplines

| ID | Discipline | ID | Discipline |
|----|------------|----|------------|
| 1 | Computer Science | 13 | Business |
| 2 | Medicine | 14 | Political Science |
| 3 | Chemistry | 15 | Economics |
| 4 | Biology | 16 | Philosophy |
| 5 | Materials Science | 17 | Mathematics |
| 6 | Physics | 18 | Engineering |
| 7 | Geology | 19 | Environmental Science |
| 8 | Psychology | 20 | Agricultural and Food Sciences |
| 9 | Art | 21 | Education |
| 10 | History | 22 | Law |
| 11 | Geography | 23 | Linguistics |
| 12 | Sociology | | |

## Input and Output

### Input

```json
{
  "file_id": "uuid-of-pdf-file"
}
```

OR

```json
{
  "structured_content_overview_id": "uuid-of-structured-content"
}
```

### Output

```json
{
  "discipline_classification_id": "uuid",
  "disciplines": [
    {
      "discipline_id": 1,
      "name": "Computer Science",
      "relevance_score": 0.95,
      "evidence": "Paper proposes novel ML algorithm..."
    }
  ],
  "confidence_score": 0.92,
  "classification_reasoning": "...",
  "paper_title": "...",
  "paper_sections": 8
}
```

## Scaffold Template

For scaffold usage and installation options, see: https://github.com/OxSci-AI/oma-scaffold
