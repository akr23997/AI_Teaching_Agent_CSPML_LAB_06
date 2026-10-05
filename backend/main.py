from pathlib import Path
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
CONTEXT_FILE = BASE_DIR / "context" / "power_electronics_context.md"

# Load .env
load_dotenv(BASE_DIR / ".env")

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "local").strip().lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini").strip()

HF_MODEL_ID = os.getenv("HF_MODEL_ID", "google/gemma-3-1b-it").strip()
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "10000"))

# OpenAI client is optional.
openai_client = None
if OPENAI_API_KEY and not OPENAI_API_KEY.startswith("PASTE_"):
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Local Gemma objects are loaded lazily on the first local request.
local_tokenizer = None
local_model = None


app = FastAPI(
    title="AI Teaching Agent - Power Electronics",
    version="2.0.0",
    description="Teaching agent with OpenAI or local Hugging Face Gemma support.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=6000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)
    mode: str = Field(default="Teach", max_length=30)
    difficulty: str = Field(default="Beginner", max_length=30)


def load_context() -> str:
    if not CONTEXT_FILE.exists():
        raise RuntimeError(f"Context file not found: {CONTEXT_FILE}")
    return CONTEXT_FILE.read_text(encoding="utf-8")


def build_instructions(context: str, mode: str, difficulty: str) -> str:
    return f"""
You are the dedicated AI Teaching Agent for the subject Power Electronics.

The following Markdown file is your authoritative subject-specific teaching context.
Use it actively when answering. Do not ignore it.

----- BEGIN SUBJECT CONTEXT -----
{context}
----- END SUBJECT CONTEXT -----

Current teaching mode: {mode}
Current student level: {difficulty}

Additional runtime teaching rules:
1. Act as a teacher, not a generic chatbot.
2. Adapt the explanation to the student's level.
3. Prefer intuition before mathematics.
4. When equations are used, define symbols and state assumptions.
5. For numerical problems, show the solution steps.
6. Ask a short check-for-understanding question when appropriate.
7. In Quiz mode, ask one question at a time and wait for the student's answer.
8. In Practice mode, provide a problem first; reveal a full solution only after the student attempts it or asks for the solution.
9. In Exam mode, format the answer so an engineering student can study or write it in an exam.
10. If the request is unrelated to Power Electronics, politely say that the configured teaching subject is Power Electronics and offer a relevant connection.
11. Never pretend to have run MATLAB/Simulink or a physical experiment unless the student provides actual results.
12. Be accurate about ideal versus practical converter behavior.
13. Do not overwhelm a beginner with unnecessary detail.
14. End normal teaching answers with either a quick check question or a suggested next topic.
""".strip()


def build_messages(request: ChatRequest, instructions: str) -> list[dict]:
    messages = [{"role": "system", "content": instructions}]

    for item in request.history[-12:]:
        if item.role in {"user", "assistant"} and item.content.strip():
            messages.append(
                {
                    "role": item.role,
                    "content": item.content[:6000],
                }
            )

    messages.append(
        {
            "role": "user",
            "content": (
                f"Teaching mode: {request.mode}\n"
                f"Student level: {request.difficulty}\n\n"
                f"Student question:\n{request.message}"
            ),
        }
    )
    return messages


def generate_with_openai(messages: list[dict]) -> str:
    if openai_client is None:
        raise RuntimeError(
            "OpenAI is selected, but OPENAI_API_KEY is not configured in .env."
        )

    # Separate system instruction from conversation for the Responses API.
    instructions = messages[0]["content"]
    conversation = messages[1:]

    response = openai_client.responses.create(
        model=OPENAI_MODEL,
        instructions=instructions,
        input=conversation,
        max_output_tokens=1200,
        store=False,
    )
    return (response.output_text or "").strip()


def load_local_gemma():
    global local_tokenizer, local_model

    if local_model is not None and local_tokenizer is not None:
        return local_tokenizer, local_model

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise RuntimeError(
            "Local Gemma dependencies are missing. Run: pip install -r requirements.txt"
        ) from exc

    # Pass HF_TOKEN when it is explicitly configured.
    token = None if (not HF_TOKEN or HF_TOKEN.startswith("PASTE_")) else HF_TOKEN

    local_tokenizer = AutoTokenizer.from_pretrained(
        HF_MODEL_ID,
        token=token,
    )

    if torch.cuda.is_available():
        local_model = AutoModelForCausalLM.from_pretrained(
            HF_MODEL_ID,
            token=token,
            device_map="auto",
            torch_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
            attn_implementation="sdpa",
        )
    else:
        # CPU fallback. It is slower, but works on a normal laptop.
        local_model = AutoModelForCausalLM.from_pretrained(
            HF_MODEL_ID,
            token=token,
            device_map="auto",
            torch_dtype=torch.float32,
            attn_implementation="sdpa",
        )

    local_model.eval()
    return local_tokenizer, local_model


def generate_with_local_gemma(messages: list[dict]) -> str:
    tokenizer, model = load_local_gemma()

    # Gemma's instruction-tuned checkpoint is used with its chat template.
    prompt_messages = []
    for msg in messages:
        prompt_messages.append(
            {
                "role": msg["role"],
                "content": [{"type": "text", "text": msg["content"]}],
            }
        )

    inputs = tokenizer.apply_chat_template(
        prompt_messages,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
        add_generation_prompt=True,
    )

    # Move tensors to the model's device.
    inputs = {key: value.to(model.device) for key, value in inputs.items()}

    with __import__("torch").inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=800,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.05,
        )

    generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
    answer = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

    if not answer:
        raise RuntimeError("Local Gemma returned an empty response.")

    return answer


def generate_answer(request: ChatRequest) -> tuple[str, str]:
    context = load_context()
    instructions = build_instructions(
        context=context,
        mode=request.mode,
        difficulty=request.difficulty,
    )
    messages = build_messages(request, instructions)

    if MODEL_PROVIDER == "local":
        return generate_with_local_gemma(messages), f"local:{HF_MODEL_ID}"

    if MODEL_PROVIDER == "openai":
        return generate_with_openai(messages), f"openai:{OPENAI_MODEL}"

    raise RuntimeError(
        "Invalid MODEL_PROVIDER in .env. Use MODEL_PROVIDER=local or MODEL_PROVIDER=openai."
    )


@app.get("/api/health")
def health():
    configured = (
        MODEL_PROVIDER == "local"
        or (MODEL_PROVIDER == "openai" and openai_client is not None)
    )

    return {
        "status": "ok",
        "provider": MODEL_PROVIDER,
        "model": HF_MODEL_ID if MODEL_PROVIDER == "local" else OPENAI_MODEL,
        "llm_configured": configured,
        "context_loaded": CONTEXT_FILE.exists(),
        "local_model_loaded": local_model is not None,
    }


@app.post("/api/chat")
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Please enter a question.")

    try:
        answer, model_name = generate_answer(request)

        return {
            "answer": answer,
            "mode": request.mode,
            "difficulty": request.difficulty,
            "provider": MODEL_PROVIDER,
            "model": model_name,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"LLM request failed: {type(exc).__name__}: {exc}",
        )


@app.get("/")
def index():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
