# Prompt Engineering Evaluation: System V1 vs System V2

## 1. Objective

The objective of this evaluation is to compare two system prompts for the WeekendYatri travel recommendation assistant.

Both prompts were tested using the same 10 questions and identical retrieved context to compare response quality, context grounding, handling of missing information, and JSON output.

## 2. Evaluation Setup

| Component | Details |
|---|---|
| LLM Provider | Groq |
| Model | Configured through `GROQ_MODEL` |
| Prompt V1 | `prompts/system_v1.txt` |
| Prompt V2 | `prompts/system_v2.txt` |
| Task Prompts | `prompts/plan_trip.txt`, `prompts/compare_places.txt` |
| Evaluation Questions | 10 |
| Total API Calls | 20 |
| Retrieval Method | TF-IDF and cosine similarity |
| Results File | `eval/prompt_results.json` |

Each question was sent to both prompts with the same context.

## 3. Prompt Comparison

### System Prompt V1

- Provides destination recommendations using retrieved context.
- Uses JSON output with `answer`, `confidence`, and `follow_up`.
- Provides relatively descriptive responses.
- May include additional details that are not explicitly supported by the retrieved context.

### System Prompt V2

- Applies stricter context-grounding instructions.
- Avoids inventing unavailable travel information.
- Communicates when information is missing.
- Uses JSON output with `answer` and `follow_up`.
- Generally produces more concise and context-focused responses.

## 4. Evaluation Results

| Evaluation criterion | System V1 | System V2 |
|---|---|---|
| JSON parsing | 10/10 valid | 10/10 valid |
| Correct Nashik destination listing | Correct | Correct |
| Adventure destination retrieval | Correct | Correct |
| Highest destination count | Correct: Ahilyanagar (8) | Correct: Ahilyanagar (8) |
| District-wise counts | Correct: 8, 7, 5 | Correct: 8, 7, 5 |
| Missing bus fare information | Correctly acknowledged as unavailable | Correctly acknowledged as unavailable |
| Pandavleni travel information | Relevant response | Relevant response |
| Heritage destination listing | Correct | Correct |
| Monsoon recommendation grounding | Included additional unsupported descriptions | Stayed closer to retrieved seasonal information |

*Note: JSON parsing validity measures whether the response could be parsed as JSON. It does not independently establish factual accuracy or complete schema compliance.*

## 5. Key Observations

### Observation 1: Context Grounding

System V2 generally followed the supplied destination information more closely.

In the monsoon recommendation question, System V1 added descriptive claims about waterfalls, misty surroundings, and cooler temperatures that were not explicitly supported by the retrieved context.

System V2 focused more closely on the `best_season` information.

### Observation 2: Handling Missing Information

Both prompts correctly acknowledged that the current bus fare from Nashik to Bhandardara was not available in the supplied dataset.

This demonstrates appropriate handling of missing information in this test.

### Observation 3: Dataset-Based Questions

Both prompts correctly answered the district-based questions:

- Ahilyanagar: 8 destinations
- Nashik: 7 destinations
- Chhatrapati Sambhajinagar: 5 destinations

The evaluation script supplied the complete dataset summary for district-count questions to avoid incomplete answers caused by top-five retrieval.

### Observation 4: Response Quality

System V1 provides a confidence field and often gives more descriptive answers.

System V2 uses a simpler output structure and generally produces more focused responses.

## 6. Limitations

- Only 10 evaluation questions were tested.
- Evaluation was performed using a single configured LLM model.
- JSON parsing was automated, but factual grounding and relevance were assessed through manual review.
- TF-IDF retrieval may not always return all relevant records.
- The evaluation does not establish performance across different LLM providers or larger datasets.
- No numerical hallucination or relevance score was calculated.

## 7. Conclusion

Based on the observed results, System Prompt V2 is the preferred prompt for WeekendYatri.

It demonstrated better context-grounding behavior in the reviewed responses, especially when recommending destinations and handling information that was not explicitly available.

System Prompt V1 remains useful as a baseline because it provides a confidence field and more descriptive answers.

Further evaluation with additional questions and systematic human review would help establish the reliability of both prompts.

## 8. Generated Evaluation Files

- `eval/questions.md` – Ten evaluation questions.
- `eval/run_prompt_evaluation.py` – Evaluation script.
- `eval/prompt_results.json` – Generated responses from both prompts.
- `eval/prompt_compare.md` – Comparative evaluation report.
- `prompts/system_v1.txt` – Baseline system prompt.
- `prompts/system_v2.txt` – Improved system prompt.
- `prompts/plan_trip.txt` – Weekend trip planning task prompt.
- `prompts/compare_places.txt` – Destination comparison task prompt.
