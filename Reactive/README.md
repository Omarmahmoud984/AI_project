# Reactive Agent — Hospital Triage System

## What this is
This is the **reactive (rule-based)** architecture for our hospital triage/doctor-info agent — a pure if/elif decision loop with **no model call at all**. Every keyword in the patient's message maps directly to a hardcoded response.

## How it works
1. The user types a message.
2. The `while True` loop checks the message against a long chain of `elif` keyword conditions (`'fire'`, `'sugar'`, `'bone'`, `'chest'`, `'poison'`, `'ahmed'`, `'bye'`, etc.), in order, top to bottom.
3. The **first** condition that matches wins — everything below it is never checked for that message.
4. Doctor-related messages either look up one specific doctor by name (printing their hours and a mocked availability status) or, if no name is matched, print the full doctor list.

## Requirements
- Python 3.x
- `doctors.json` in the same directory as the script (no API key or external package needed — this version makes no model calls)

`doctors.json` format:
```json
{
  "Dr Ahmed": "9 AM - 5 PM",
  "Dr Sara": "10 AM - 6 PM",
  "Dr Mohamed": "8 AM - 4 PM",
  "Dr Nour": "11 AM - 7 PM",
  "Dr Yasmine": "9 AM - 3 PM"
}
```

## Running it
```
python reactive_agent.py
```
Type a message and press enter. Type a message containing `bye` to exit.

## Known limitations (this is the point of the reactive version)
- **Order-dependent matching, not true understanding.** Keywords are checked top-to-bottom and the first match wins, so message content the assignment cares about — like negation — isn't handled: *"I don't have a fever"* still matches `'fever'` and gets routed to general medicine.
- **No handling of multiple symptoms at once.** *"My chest hurts and I'm bleeding"* only ever hits the first matching branch (`chest`/`heart` → cardiology), even though bleeding is arguably more urgent.
- **Fragile keyword collisions.** The `'head' in user_inp and 'ache' not in user_inp` check is a patch for the fact that "headache" would otherwise wrongly trigger the head-injury/neurology branch — a sign of how quickly plain keyword matching needs special-casing.
- **Doctor availability is mocked** — `get_dr_stat()` returns a random True/False, not real data.
- **`display_all_DRs` and `get_dr_stat` print instead of returning values**, which makes this harder to unit test or reuse outside the interactive loop.
- **No memory across turns.** Each message is evaluated in isolation; the agent can't use anything said earlier in the conversation to inform a later decision — which is exactly the kind of case the constrained ReAct version is meant to handle.

## Architecture notes (for the comparison table)
- **Model calls per request:** 0
- **Cost:** free, no API usage
- **Latency:** effectively instant (dictionary/keyword lookup)
- **Tradeoff:** cheapest and fastest option, but brittle — breaks on negation, multiple symptoms, and any input the original keyword list didn't anticipate.
