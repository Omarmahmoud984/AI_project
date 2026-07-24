# MedCare Hospital — Emergency Triage & Doctor Info Agent

## The Company & Problem

MedCare is a hospital that runs a walk-in/emergency chat intake system. Before a
patient sees anyone, someone (or something) has to answer a simple but high-stakes
question: **where does this patient need to go, right now?**

Patients type in free-form messages describing symptoms, or ask about a specific
doctor's availability and working hours. A human triage assistant would normally
read the message, weigh the symptoms, and route the patient to the right
department — burns, cardiology, trauma, neurology, and so on — or point them to
the right doctor if that's what they're asking for.

This is not a job for a simple lookup script. Patients don't type clean, structured
input — they type things like *"I don't have any bone problems"* or *"chest pain
and I'm bleeding"*, and the system has to understand **meaning**, not just match
keywords, to route them correctly. A wrong or careless routing decision in a
hospital context has real consequences, which is exactly why this problem is worth
building an agent for instead of a static form.

## Why This Needs an Agent (Not Just a Script)

A fixed script can only match literal keywords. It can't tell "I have chest pain"
from "I don't have chest pain," it can't weigh two symptoms mentioned in the same
message, and it can't adapt when a patient phrases something in a way nobody
anticipated. An agent — with real language understanding — can.

We built the same problem four separate times, once per architecture, to feel
firsthand where a simple rule-based system breaks, what changes when a model is
given free rein, and how much control is actually needed to get something safe and
production-worthy.

## Folder Structure

```
reactive/              pure if/elif keyword matching, no model call
unconstrained_react/   free-form LLM reasoning + tool use, no limits
routing/                single classification call + hardcoded routing logic
constrained_react/     schema-validated, tool-restricted, step-limited ReAct loop
```

Each folder is runnable on its own — see the note at the top of each script for
what it expects (model/provider, environment variable for the API key, etc.).

## The Four Architectures

### 1. Reactive (`reactive/`)
A pure if/elif keyword-matching loop against the patient's message, plus a
hardcoded doctor-lookup against `doctors.json`. No model call at all.

**Where it broke (our own test cases):**
- **Negation blindness** — *"I don't have bone problems"* still routes to the bone
  department; *"my sugar level is good"* still triggers the diabetes warning. The
  system can't tell affirmation from denial, only whether a keyword is present.
- **First-match-wins** — a message like *"chest pain and I'm bleeding"* only ever
  triggers the first matching branch (cardiology), silently ignoring the more
  urgent trauma symptom.
- **Fake availability** — doctor availability is a random `True`/`False` coin
  flip, completely disconnected from real data. Asking twice can give
  contradictory answers.

### 2. Unconstrained LLM-Powered Agent (`unconstrained_react/`)
*(in progress)*

A free-form ReAct-style loop: the model reads the patient's message and decides
for itself — with no schema, no tool allow-list, and no step limit — which tools
to call (e.g. check symptoms, look up a doctor's hours, check availability) and
when it's satisfied enough to answer.

**What we expect to test once this is built** (same fixed input set as the other
three agents, per the assignment's apples-to-apples requirement):
- `"I don't have bone problems"`
- `"my sugar level is good"`
- `"I don't want Dr Ahmed"`
- `"chest pain and I'm bleeding"`

**What we're watching for**, based on how this architecture is expected to behave:
- Whether it correctly handles negation and multi-symptom messages the way the
  routing agent does, but *without* a fixed category forcing the answer.
- Whether letting the model choose its own tools and stopping point introduces new
  failure modes the routing agent doesn't have — e.g. calling tools unnecessarily,
  looping, or answering with unwarranted confidence on an ambiguous message like
  `"hahaha"` or `"my cat is sick"`.
- Cost, latency, and token usage compared to the single-call routing agent, since
  this version can make an unbounded number of model calls per request.

### 3. Deterministic Routing Agent (`routing/`)
A single Gemini classification call sorts the patient's message into one of a
fixed set of categories (`BURNS`, `DIABETES`, `DOCTOR_INFO`, etc.). Everything
after that — the department message lookup, the doctor-info branch — is ordinary,
testable Python.

Unlike the reactive version, this correctly handles negation and multi-symptom
messages because the model actually reads for meaning rather than matching
substrings.

### 4. Constrained ReAct Agent (`constrained_react/`)
Same reasoning loop as the unconstrained version, but every step is
schema-validated, tool calls are restricted to an approved allow-list, and the
loop is bounded by a fixed step budget. The agent can chain multiple tool calls
(e.g. check symptoms, then check a specific doctor's availability) while
remaining predictable and safe — something neither the reactive nor the routing
agent can do, since both are limited to a single decision per message.

**Where the constraints live:**

| Component | Location |
|---|---|
| Validation Schema | `schema.py` |
| Tool Allow-List | `constrain.py` (`TOOL_ALLOWLIST`) |
| Maximum Steps | `constrain.py` (`MAX_STEPS = 6`) |

**Setup:**
```bash
pip install -r requirements.txt
```
Create a `.env` file with:
```text
GEMINI_API_KEY=your_key_here
```
Run with:
```bash
python constrain.py
```
- **Provider:** Google AI Studio
- **Model:** `gemini-3.5-flash-lite` (change the `MODEL` constant in `constrain.py` to use a different Gemini model)

**Test cases and expected behavior:**
- *"my chest hurts but I don't have a fever, is dr sara free right now?"* — the
  agent has to analyze the symptom, route to the right department, check Dr.
  Sara's availability, and end in a `final_answer` or `escalate` — a genuine
  multi-step case the routing agent can't handle in one call.

  **Actual result:** the agent recognized chest pain as a potential emergency and
  went straight to `escalate` in a single step (1/6 steps used), skipping the
  Dr. Sara availability check entirely — reasoning that a life-threatening
  symptom shouldn't wait on a scheduling lookup. Latency 1.05s, 243 input /
  84 output tokens (~$0.00028). This is a real, worth-discussing tradeoff: the
  constraint that makes the agent decisive and fast on urgent cases is the same
  thing that made it skip the patient's actual question. Worth deciding — and
  saying out loud in the presentation — whether that's the right call or a gap.
- *"my stomach hurts and I am bleeding"* — expected to trigger immediate
  `escalate`.
- *"my cat is sick"* — expected to inform the user the hospital only handles
  human patients, rather than trying to force a department match.
- *"hahaha"* — expected to ask for clarification rather than guessing.

**Safety notes:**
- API keys live in `.env`, excluded from GitHub via `.gitignore`.
- Every reasoning step is schema-validated.
- Only allow-listed tools can execute.
- Reasoning is capped at 6 steps.
- Every interaction must terminate in either `final_answer` or `escalate`.

## Comparison Table

| Architecture | Model calls / request | Tokens (in/out) | Cost per call | Latency | What broke |
|---|---|---|---|---|---|
| Reactive | 0 | — | $0 | ~instant (0.0002s) | Negation blindness, first-match-wins, fake random availability |
| Unconstrained ReAct | 1 (single-step test) | 61 / 92 | ~$0.000248 | 0.85s | Longest output of the three by far — nothing caps response length, so it's the most expensive per call despite making the fewest calls. Multi-step tool-use behavior not yet tested. |
| Routing | 1 | 133 / 3 | ~$0.000047 | 0.86s | Cheapest and fastest — correctly handles negation via prompt design; can't chain reasoning across multiple facts (e.g. symptom + doctor lookup) in one call. |
| Constrained ReAct | 1 of 6 available (`MAX_STEPS`) | 243 / 84 | ~$0.00028 | 1.05s | Escalated on chest pain in a single step but skipped the patient's doctor-availability question to do it — the safety constraint traded off against completeness. MAX_STEPS exhaustion and allow-list rejection cases not yet tested. |

*(Pricing based on Gemini 3.5 Flash-Lite: $0.30 per million input tokens, $2.50 per
million output tokens. Numbers above are from single-request tests against one
test case each; full runs across the shared test-input set are still in progress.)*

## Test Inputs Used Across All Four Agents

- `"I have a bad burn on my hand"` — easy case
- `"I don't have bone problems"` — negation
- `"my sugar level is good"` — negation
- `"I don't want Dr Ahmed"` — negation + doctor lookup
- `"chest pain and I'm bleeding"` — multi-symptom collision

## Team

*(commit history / contributions to be added)*
