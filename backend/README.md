# Virelya Backend

FastAPI backend for Virelya Poetry Muse.

- `/suggest-line`: POST endpoint for next-line suggestions.
- Uses Hugging Face Transformers (GPT-2).
- Loads poems from `../data/darshan_poems.json`.
