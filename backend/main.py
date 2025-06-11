from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import json
import os

# --- Load Poems Dataset ---
POEMS_PATH = os.path.join(os.path.dirname(__file__), '../data/darshan_poems.json')
with open(POEMS_PATH, 'r') as f:
    POEMS = json.load(f)

# --- FastAPI App ---
app = FastAPI()

# --- Request/Response Models ---
class SuggestLineRequest(BaseModel):
    lines: List[str]
    top_k: int = 3

class SuggestLineResponse(BaseModel):
    suggestions: List[str]

# --- Load GPT-2 Model ---
MODEL_NAME = 'gpt2'
tokenizer = GPT2Tokenizer.from_pretrained(MODEL_NAME)
model = GPT2LMHeadModel.from_pretrained(MODEL_NAME)
model.eval()
if torch.cuda.is_available():
    model.to('cuda')

# --- Helper: Build Prompt ---
def build_prompt(user_lines: List[str]) -> str:
    # Use up to 3 user lines, then a few lines from dataset as style context
    prompt = "Given these lines, suggest the next poetic line.\n"
    # Add user lines
    prompt += "\n".join(user_lines)
    prompt += "\n"
    # Add 1-2 random lines from the dataset for style
    import random
    poem = random.choice(POEMS)
    style_lines = random.sample(poem['content'], min(2, len(poem['content'])))
    prompt += "\n".join(style_lines)
    prompt += "\n"
    return prompt

# --- Endpoint: /suggest-line ---
@app.post("/suggest-line", response_model=SuggestLineResponse)
def suggest_line(req: SuggestLineRequest):
    if not req.lines or not all(isinstance(line, str) for line in req.lines):
        raise HTTPException(status_code=400, detail="Invalid input lines.")
    prompt = build_prompt(req.lines)
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    if torch.cuda.is_available():
        input_ids = input_ids.to('cuda')
    # Generate up to 50 tokens, sample top_k
    outputs = model.generate(
        input_ids,
        max_length=input_ids.shape[1] + 30,
        num_return_sequences=req.top_k,
        do_sample=True,
        top_k=40,
        temperature=0.9,
        pad_token_id=tokenizer.eos_token_id
    )
    suggestions = []
    for out in outputs:
        generated = tokenizer.decode(out[input_ids.shape[1]:], skip_special_tokens=True)
        # Only take the first line
        next_line = generated.strip().split('\n')[0]
        if next_line and next_line not in suggestions:
            suggestions.append(next_line)
    return SuggestLineResponse(suggestions=suggestions[:req.top_k])
