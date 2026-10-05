# AI Teaching Agent — Power Electronics Tutor

This project implements the assignment:

> Develop an AI-powered Teaching Agent for any subject of your choice.

**Chosen subject:** Power Electronics / Electrical Engineering

The system is deliberately more than a generic chatbot. It loads `context/power_electronics_context.md` on every request and uses the subject knowledge + teaching instructions to produce structured explanations, examples, checks for understanding, and practice questions.

## What is included

- `frontend/` — interactive student web interface
- `backend/` — FastAPI server and LLM integration
- `context/power_electronics_context.md` — subject-specific knowledge and teaching instructions
- `.env` — API key/configuration placeholder
- `.env.example` — safe template
- `docs/PROJECT_PLAN.md` — project plan
- `docs/ARCHITECTURE.md` — block diagram and system architecture
- `requirements.txt` — Python dependencies
- `start.bat` — one-click Windows launcher
- `start.ps1` — PowerShell launcher
- `backend/main.py` — API + static frontend server

## Requirements

Recommended:

- Windows 10/11
- Python 3.11 or 3.12
- Internet connection
- An OpenAI API key

Python 3.14 may work, but Python 3.11/3.12 is recommended for the smoothest dependency installation.

## 1. Open the project

Extract the ZIP file. Then open the extracted folder in VS Code.

The folder should look like:

```text
AI_Teaching_Agent_Power_Electronics
│
├── .env
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── start.bat
├── start.ps1
│
├── backend
│   └── main.py
│
├── context
│   └── power_electronics_context.md
│
├── docs
│   ├── ARCHITECTURE.md
│   └── PROJECT_PLAN.md
│
└── frontend
    ├── index.html
    ├── style.css
    └── app.js
```

## 2. Add your API key

Open `.env`.

Replace:

```text
PASTE_YOUR_OPENAI_API_KEY_HERE
```

with your real API key.

Example:

```text
OPENAI_API_KEY=your_real_key_here
OPENAI_MODEL=gpt-5-mini
```

Do not put quotation marks around the key.

The `.env` file is ignored by Git using `.gitignore`.

## 3. Install dependencies

### Easiest method on Windows

Double-click:

```text
start.bat
```

The script creates a virtual environment, installs dependencies, and starts the server.

### Manual VS Code method

Open VS Code Terminal:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Then:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Start the application

Run:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

The FastAPI backend serves the frontend, so you do not need a separate frontend server.

## 5. Test the system

Try questions such as:

- What is a power electronic converter?
- Explain a buck converter step by step.
- Why is PWM used in a DC-DC converter?
- Give me a numerical problem on a buck converter.
- I do not understand duty cycle. Teach it with an analogy.
- Quiz me on three-phase inverters.

The agent should:

1. Identify the learning goal.
2. Explain the concept at an appropriate level.
3. Use the Power Electronics context file.
4. Give an example or equation when useful.
5. Ask a short check-for-understanding question.
6. Suggest a next learning step.

## Assignment requirement mapping

| Assignment requirement | Implementation |
|---|---|
| Frontend | `frontend/index.html`, `style.css`, `app.js` |
| Backend | FastAPI in `backend/main.py` |
| LLM integration | OpenAI Responses API |
| Subject context | `context/power_electronics_context.md` |
| Context used for responses | Backend reads context and sends it as teaching instructions |
| `.env` | API key and model configuration |
| Project plan | `docs/PROJECT_PLAN.md` |
| Block diagram | `docs/ARCHITECTURE.md` |
| README | This file |
| Teaching agent, not generic chatbot | Structured tutor prompt + learning mode + quiz/check-for-understanding behavior |

## How the context file works

The backend reads:

```text
context/power_electronics_context.md
```

at startup.

It then creates a system-level teaching instruction from that file.

Therefore, changing the context file changes the subject knowledge and teaching style without changing the frontend.

For example, you can replace the context with:

- Embedded Systems
- Signals and Systems
- Control Systems
- Mathematics
- Physics

and adapt the agent to that subject.

## API endpoints

### Health

```text
GET /api/health
```

Returns server status and whether an API key appears configured.

### Chat

```text
POST /api/chat
```

Example JSON:

```json
{
  "message": "Explain a buck converter",
  "history": [],
  "mode": "Teach",
  "difficulty": "Beginner"
}
```

## Troubleshooting

### `ModuleNotFoundError: No module named fastapi`

Run:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### PowerShell says scripts are disabled

Use Command Prompt instead:

```cmd
.venv\Scripts\activate.bat
```

Then install requirements.

### API key error

Check `.env` and make sure:

```text
OPENAI_API_KEY=...
```

contains a valid API key.

Also make sure the API account has API access/billing configured.

### Model not found

Change:

```text
OPENAI_MODEL=gpt-5-mini
```

to a model available to your API account.

### Port 8000 is already in use

Run:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8010
```

Then open:

```text
http://127.0.0.1:8010
```

## Important security note

Never upload a real `.env` containing your API key to GitHub, WhatsApp, a public drive, or your assignment submission if the submission will be publicly accessible.

For a college submission, submit `.env` with the placeholder and keep your real key private.

## Suggested demonstration for your viva

1. Open the tutor.
2. Select `Beginner`.
3. Ask: "What is a buck converter?"
4. Show the structured teaching answer.
5. Ask: "Give me a numerical problem."
6. Answer it.
7. Ask: "Quiz me."
8. Show the quiz/check-for-understanding behavior.
9. Open `context/power_electronics_context.md` and explain that the agent is grounded by the subject-specific teaching context.
10. Open `docs/ARCHITECTURE.md` to explain the frontend → backend → context + LLM → response flow.

## Reference

The implementation uses the OpenAI Python SDK and the Responses API. The current SDK supports `client.responses.create(...)` and `response.output_text`; the model is configurable through `.env`.


## Local Hugging Face Google Gemma option

This project also supports a **local LLM** using Google's Gemma 3 1B instruction-tuned model through Hugging Face Transformers.

The default local model is:

```text
google/gemma-3-1b-it
```

Hugging Face provides an official Transformers usage example for this checkpoint. Gemma access may require accepting Google's Gemma usage conditions on Hugging Face. The 1B model is the recommended starting point for a normal laptop. citeturn1search0turn1search1

### Configure local Gemma

Open `.env`:

```text
MODEL_PROVIDER=local
HF_MODEL_ID=google/gemma-3-1b-it
HF_TOKEN=YOUR_HUGGING_FACE_TOKEN
```

You do not need `OPENAI_API_KEY` when using the local provider.

Install the extra packages:

```powershell
pip install -r requirements.txt
```

Then start:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

The first request downloads/loads Gemma, so it may take longer than later requests.

### Use Hugging Face CLI instead of putting the token in `.env`

You can authenticate with:

```powershell
hf auth login
```

and then leave `HF_TOKEN` empty.

### Switching providers

Local Gemma:

```text
MODEL_PROVIDER=local
HF_MODEL_ID=google/gemma-3-1b-it
```

OpenAI:

```text
MODEL_PROVIDER=openai
OPENAI_MODEL=gpt-5-mini
OPENAI_API_KEY=YOUR_OPENAI_KEY
```

Restart the server after changing `.env`.

For a larger local model, you can try `google/gemma-3-4b-it`, but it needs substantially more memory than the 1B model. Gemma 3 is supported through Transformers, and Hugging Face documents quantization options for reducing memory use. citeturn0search1turn1search2

See `LOCAL_GEMMA_GUIDE.md` for the complete step-by-step setup.
