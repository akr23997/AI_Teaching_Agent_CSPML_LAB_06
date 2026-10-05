# Project Plan

## 1. Project title

**AI-Powered Teaching Agent for Power Electronics**

## 2. Objective

Build an AI teaching assistant that teaches Power Electronics concepts interactively instead of acting as a generic question-answering chatbot.

## 3. Functional requirements

### Student interface
- Ask questions in natural language.
- Select learning level.
- Select learning mode.
- View conversation history.
- Clear the current conversation.

### Teaching agent
- Use the subject context file.
- Explain concepts step by step.
- Prefer intuition before equations.
- Give examples.
- Check student understanding.
- Generate practice questions.
- Adapt explanations to beginner/intermediate/advanced level.
- Avoid pretending that unrelated questions are Power Electronics questions.

### Backend
- Receive student requests.
- Load subject context.
- Build teaching instructions.
- Call the LLM.
- Return the response to the frontend.
- Handle errors safely.

## 4. Technology stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python + FastAPI
- LLM: OpenAI Responses API
- Configuration: `.env`
- Context: Markdown
- Server: Uvicorn

## 5. Development phases

### Phase 1 — Planning
Define the subject, learning objectives, interface and architecture.

### Phase 2 — Context design
Create subject-specific knowledge and teaching rules in Markdown.

### Phase 3 — Backend
Create FastAPI endpoints and connect the OpenAI SDK.

### Phase 4 — Frontend
Create the student chat interface.

### Phase 5 — Integration
Connect frontend requests to the backend and LLM.

### Phase 6 — Testing
Test:
- Basic explanation
- Numerical question
- Quiz generation
- Different difficulty levels
- Empty input
- API errors
- Context grounding

### Phase 7 — Demonstration
Show the complete learning workflow during evaluation.

## 6. Success criteria

The project is successful when:

1. The student can ask a Power Electronics question.
2. The backend receives it.
3. The context file is incorporated into the teaching instruction.
4. The LLM generates a teaching-oriented response.
5. The response is displayed in the frontend.
6. The student can continue the conversation.
7. The system can switch teaching modes.

## 7. Future improvements

- User login
- Student progress tracking
- Topic-wise quizzes
- Automatic scoring
- PDF/lecture-note ingestion
- Retrieval-Augmented Generation (RAG)
- Diagrams generated for circuits
- Voice input/output
- Teacher dashboard
