# WeekendYatri RAG Configuration Evaluation

## Evaluation Setup

- Evaluation questions: 15
- Answerable questions: 14
- Unanswerable questions: 1
- Embedding model: all-MiniLM-L6-v2
- Vector database: ChromaDB
- Generation model: Groq

## Configuration Comparison

| Metric | Configuration A | Configuration B |
|---|---:|---:|
| Chunk size | 150 | 300 |
| Top-k | 3 | 5 |
| Stored chunks | 22 | 21 |
| Retrieval recall | 0.7381 | 0.9167 |
| Answer keyword coverage | 0.6667 | 0.7976 |
| Citation coverage | 0.7444 | 0.6267 |
| Unknown answer accuracy | 1.0 | 1.0 |
| Average response time (seconds) | 3.4645 | 1.2274 |
| Overall score | 0.7441 | 0.8313 |

## Winner

**Configuration B** achieved the higher weighted score (0.8313).

## Scoring Method

- Retrieval keyword recall: 40%
- Answer keyword coverage: 30%
- Citation coverage: 20%
- Unknown answer accuracy: 10%

The overall score is a project-defined evaluation metric, not a standard benchmark.

## Notes

- Configuration A metrics were preserved from its completed terminal evaluation.
- Configuration B results were saved after each completed question.
- Configuration B response times exclude previous interrupted attempts.
- Lower response time is preferable.
