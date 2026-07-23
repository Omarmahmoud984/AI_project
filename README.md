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
reactive/            pure if/elif keyword matching, no model call
unconstrained_react/  free-form LLM reasoning + tool use, no limits
routing/              single classification call + hardcoded routing logic
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

### 3. Deterministic Routing Agent (`routing/`)
A single Gemini classification call sorts the patient's message into one of a
fixed set of categories (`BURNS`, `DIABETES`, `DOCTOR_INFO`, etc.). Everything
after that — the department message lookup, the doctor-info branch — is ordinary,
testable Python.

Unlike the reactive version, this correctly handles negation and multi-symptom
messages because the model actually reads for meaning rather than matching
substrings.

### 4. Constrained ReAct Agent (`constrained_react/`)
*(in progress)*

## Comparison Table

| Architecture | Model calls / request | Rough cost per call | Latency | What broke |
|---|---|---|---|---|
| Reactive | 0 | $0 | ~instant | Negation blindness, first-match-wins, fake random availability |
| Unconstrained ReAct | TBD | TBD | TBD | TBD |
| Routing | 1 | ~$0.0001–0.0005 (Gemini Flash-tier pricing) | low (single call) | TBD — testing negation cases in progress |
| Constrained ReAct | TBD | TBD | TBD | TBD |

*(Cost/latency numbers to be filled in from `usage_metadata` logging once all four
architectures are tested against the same fixed set of inputs.)*

## Test Inputs Used Across All Four Agents

- `"I don't have bone problems"` — negation
- `"my sugar level is good"` — negation
- `"I don't want Dr Ahmed"` — negation + doctor lookup
- `"chest pain and I'm bleeding"` — multi-symptom collision

## Team

*(commit history / contributions to be added)*
