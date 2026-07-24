# Constrained ReAct Agent

This implementation simulates a hospital triage assistant using the Constrained ReAct architecture. The agent follows a reasoning loop similar to an unconstrained agent, but every action is validated through a schema, restricted to an approved tool allow-list, and bounded by a fixed step budget.

---

## Project Overview

The agent is responsible for analyzing patient requests and deciding whether to:

- Provide a final answer.
- Escalate the case to a human.
- Chain multiple tool calls when necessary.

Unlike Reactive or Routing agents, this implementation can perform multi-step reasoning while remaining predictable and safe.

---

## Constraints

| Component | Location |
|----------|----------|
| Validation Schema | `schema.py` |
| Tool Allow-List | `constrain.py` (`TOOL_ALLOWLIST`) |
| Maximum Steps | `constrain.py` (`MAX_STEPS = 6`) |

---

## How to Run

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file and add your Google AI Studio API key:

```text
GEMINI_API_KEY=your_key_here
```

3. Run the application:

```bash
python constrain.py
```

---

## Model and Provider

- **Provider:** Google AI Studio
- **Model:** `gemini-3.5-flash-lite`

To use a different Gemini model, simply modify the `MODEL` constant inside `constrain.py`.

---

## Example Test Cases

### Tricky Input

```text
my chest hurts but I don't have a fever, is dr sara free right now?
```

This input forces the agent to:

1. Analyze the symptoms.
2. Route the patient to the appropriate department.
3. Check Dr. Sara's availability.
4. Produce a `final_answer` or `escalate` if needed.

This demonstrates why the Constrained ReAct architecture is more capable than Reactive and Deterministic Routing approaches for multi-step decision making.

### Additional Examples

```text
my stomach hurts and I am bleeding
```

Expected behavior:

- Immediate escalation for urgent care.

```text
my cat is sick
```

Expected behavior:

- Inform the user that the hospital only handles human patients.

```text
hahaha
```

Expected behavior:

- Request clarification from the user.

---

## Notes

- All API keys are stored in `.env` and excluded from GitHub using `.gitignore`.
- The agent enforces schema validation for every reasoning step.
- Only approved tools can be executed.
- The reasoning process is limited to a maximum of six steps.
- Every interaction must terminate with either `final_answer` or `escalate`.
