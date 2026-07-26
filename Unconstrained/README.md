# Unconstrained LLM-Powered Agent — Hospital Triage System

## What this is
This is the **unconstrained LLM-powered** architecture for our hospital triage/doctor-info agent — a free-form chat loop where the model reasons about the patient's message and decides on its own how to respond. No fixed categories, no schema, no tool allow-list, and no step limit.

## How it works
1. `doctors.json` is loaded once at startup.
2. A mocked availability flag (`True`/`False`, random per doctor) is rolled once per session — same mocked-data approach as the reactive and routing agents.
3. Every turn, the full doctor info (hours + availability) and the running conversation history are folded into one prompt and sent to Gemini.
4. The model decides freely — in plain natural language, not a fixed format — how to respond: what department to suggest, whether to answer a doctor question, whether to ask a follow-up. There's no tool-calling loop, no JSON output requirement, and no cap on how it reasons.

## Requirements
- Python 3.x
- `google-genai` package
- `doctors.json` in the same directory
- A Gemini API key set as an environment variable

Install:
```
pip install google-genai
```

## Setup
```
export GEMINI_API_KEY=your_key_here
```
The key is read via `os.getenv("GEMINI_API_KEY")` — never pasted into the script — per the assignment's guardrail against committing API keys.

## Running it
```
python unconstrained_agent.py
```
Type a message and press enter. Type `quit` to exit.

## Known limitations / what broke
- **The model initially refused to use the doctor data it was given.** Even with `doctors.json` passed directly into every prompt, the model would sometimes answer "I don't have access to real-time doctor information" — a known LLM caution habit, not a data problem. Fixed by explicitly telling the model in the system prompt that the JSON provided *is* its live access to doctor data, and that it should never claim otherwise. This is a good demonstrable "new problem that showed up" for the presentation: giving the model free rein doesn't guarantee it will actually use the tools/data it's handed.
- **Doctor availability is mocked** — rolled once per session as `True`/`False`, not real data, same as the other three agents.
- **No step limit or output length cap.** In side-by-side token tests, this architecture's response was the longest and most expensive per call of the three tested (routing, unconstrained, constrained) on the same input, because nothing constrains how much the model says.
- **No schema validation.** Because responses are free-form natural language, there's no structured way to check whether the model actually answered the question, made a real recommendation, or wandered off-topic — this has to be checked by eye, which doesn't scale the way the routing or constrained agents' outputs do.
- **No tool allow-list or true multi-step tool use in this version.** This build is a single-call-per-turn chat loop, not a full ReAct tool-calling agent — it reasons over the doctor data given in the prompt rather than calling a `check_doctor_availability`-style function. A fuller ReAct version (actual function calling, multi-step tool chains) is a possible next step if the presentation calls for a stronger contrast with the constrained ReAct agent.

## Architecture notes (for the comparison table)
- **Model calls per request:** 1 per user turn (no internal tool-call loop in this version)
- **Cost:** highest per-call cost of the three measured so far — unconstrained output length drives this, not call count
- **Latency:** comparable to routing on a single turn, since both are one call — but conversation history grows every turn, so later turns cost more than early ones
- **Tradeoff:** most flexible and natural-sounding of the four architectures, but the least predictable — no guarantee it stays on-topic, uses the data it's given, or produces an answer in a consistent shape.
