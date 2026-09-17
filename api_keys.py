import os

API_KEYS = [
    {"provider": "groq", "key": os.environ.get("GROQ_KEY", ""),
     "url": "https://api.groq.com/openai/v1/chat/completions",
     "model": "llama-3.1-8b-instant", "priority": 1,
     "cooldown": 0, "uses": 0, "errors": 0},
    
    {"provider": "gemini", "key": os.environ.get("GEMINI_KEY", ""),
     "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
     "model": "gemini-1.5-flash", "priority": 2,
     "cooldown": 0, "uses": 0, "errors": 0},
    
    {"provider": "github", "key": os.environ.get("GITHUB_TOKEN", ""),
     "url": "https://models.github.ai/inference/chat/completions",
     "model": "openai/gpt-4o", "priority": 3,
     "cooldown": 0, "uses": 0, "errors": 0},
    
    {"provider": "openrouter", "key": os.environ.get("OPENROUTER_KEY", ""),
     "url": "https://openrouter.ai/api/v1/chat/completions",
     "model": "meta-llama/llama-3.3-70b-instruct:free", "priority": 4,
     "cooldown": 0, "uses": 0, "errors": 0},
]
