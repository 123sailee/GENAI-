# How Large Language Models (LLMs) Work

## 1. What is an LLM?

A Large Language Model (LLM) is an artificial intelligence model trained on a large amount of text data. It learns patterns in language and uses those patterns to understand prompts and generate responses.

Examples include GPT, Gemini, and Llama.

## 2. How does an LLM work?

The basic process is:

**Prompt → Tokens → Model → Next token**

1. **Prompt:** The user enters a question or instruction.
2. **Tokens:** The text is divided into smaller units called tokens. A token can be a word, part of a word, or punctuation.
3. **Model:** The tokens are processed by the model. Transformer architecture and attention mechanisms help the model understand relationships between tokens.
4. **Next token:** The model predicts the next likely token based on the previous context.

This process repeats until the response is complete or a stopping condition is reached.

## 3. What is Tokenization?

Tokenization is the process of converting text into smaller units called tokens.

For example:

`I love travelling`

A tokenizer may divide this sentence into tokens such as:

`["I", "love", "travelling"]`

The exact tokens depend on the tokenizer used by the model.

## 4. What is a Transformer?

A Transformer is a neural network architecture widely used in modern LLMs.

Its attention mechanism helps the model identify relationships between different tokens in the input.

For example, in a sentence, attention helps the model understand which words are related to one another.

## 5. What is Next-Token Prediction?

LLMs generally generate text by predicting one token at a time.

For example:

Prompt: `WeekendYatri helps users discover`

Possible next token: `destinations`

The model then uses the updated context to predict another token.

## 6. What is a Context Window?

A context window is the amount of text or tokens a model can consider during a particular interaction.

If the conversation exceeds the model's context limit, some earlier information may no longer be available to it.

## 7. What are LLM Hallucinations?

Hallucinations occur when an LLM generates information that sounds convincing but is incorrect, unsupported, or fabricated.

For WeekendYatri, this is important because the application should not invent destination details, travel costs, opening hours, or transport availability.

We should use reliable sources and clearly indicate when information is unavailable.

## 8. Limitations of LLMs

- They can generate incorrect information.
- They may not have access to current information.
- Their responses depend on the quality and relevance of the input.
- They have a limited context window.
- They can produce biased or misleading responses.

## 9. Application in WeekendYatri

WeekendYatri can use an LLM to understand natural-language travel requests.

For example:

`Suggest an adventure destination near Nashik for a winter weekend.`

The application can identify the user's interests, season, and location, then use the destination dataset to retrieve relevant places.

The LLM should not invent destinations or unsupported travel information.