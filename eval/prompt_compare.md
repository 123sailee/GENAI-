# WeekendYatri Prompt Comparison

## Objective
Compare two system prompts for the WeekendYatri AI travel assistant.

## Prompt V1 – Basic Travel Assistant
- Provides destination recommendations.
- Uses retrieved destination information.
- Follows a JSON response format.
- Avoids inventing travel information.

## Prompt V2 – Context-Aware Travel Assistant
- Uses only retrieved destination records.
- Matches destinations to budget, season, category and travel time when supported by context.
- Explains why recommendations match user preferences.
- Clearly communicates missing information.
- Returns structured JSON with answer, confidence and follow_up.

## Evaluation Criteria

| Criteria | Prompt V1 | Prompt V2 |
|---|---|---|
| Context grounding | To be tested | To be tested |
| Relevance | To be tested | To be tested |
| JSON validity | To be tested | To be tested |
| Follow-up quality | To be tested | To be tested |
| Hallucination control | To be tested | To be tested |

## Evaluation Questions

1. Suggest adventure destinations for winter.
2. Suggest heritage destinations in Nashik.
3. Recommend destinations within a budget of ₹2,000.
4. Suggest destinations for the monsoon season.
5. Recommend a destination not present in the database.

## Expected Outcome

Prompt V2 should provide more context-aware recommendations,
better handling of missing information and improved grounding.

Actual performance must be verified by testing both prompts.