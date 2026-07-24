# Routing Agent — Hospital Triage System

## What this is
This is the **deterministic routing** architecture for our hospital triage/doctor-info agent. One constrained model call classifies the patient's message into a fixed category; everything after that is plain, hardcoded, testable Python.

## How it works
1. The user types a message describing a symptom or asking about a doctor.
2. `classify()` sends the message to Gemini along with `ROUTING_PROMPT`, which forces the model to return exactly one label from a fixed list of categories (e.g. `CARDIOLOGY`, `BURNS`, `DOCTOR_INFO`, `UNKNOWN`, etc.).
3. `handle_message()` takes that label and looks up a hardcoded response in `ROUTE_MAP` — no further model calls.
4. If the category is `DOCTOR_INFO`, the code keyword-matches a doctor's name in the message and looks up their working hours in `doctors.json`, then reports a (currently mocked) availability status.

## Requirements
- Python 3.x
- `google-genai` package
- A Gemini API key
- `doctors.json` in the same directory as the script

Install the dependency:
```
pip install google-genai
```

## Setup
1. Set your Gemini API key in the `API_KEY` variable at the top of the script.
2. Make sure `doctors.json` is present, formatted like:
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
python routing_agent.py
```
Type a message and press enter. Type `quit` to exit.

## Categories the classifier can return
`BURNS, DIABETES, ORTHOPEDIC, OPHTHALMOLOGY, CARDIOLOGY, TOXICOLOGY, TRAUMA, NEUROLOGY, ALLERGY, MATERNITY, GASTROENTEROLOGY, GENERAL_MEDICINE, DERMATOLOGY, DOCTOR_INFO, GREETING, THANKS, GOODBYE, UNKNOWN`

The prompt is designed to avoid false positives on negated symptoms (e.g. "I don't have chest pain" is *not* classified as `CARDIOLOGY`).

## Known limitations
- **Doctor availability is mocked** — `get_dr_stat()` returns a random True/False, not real data.
- **No error handling on the API call** — if the Gemini request fails or times out, the script will crash instead of degrading gracefully.
- **Doctor name matching is a simple substring check** on the raw message, run *after* the model has already classified the intent as `DOCTOR_INFO` — this is intentional (keeps the lookup deterministic and testable) rather than asking the model to extract the name itself.
- **API key is currently pasted directly into the script** — fine for local-only runs, but should move to a `.env` file (via `python-dotenv`) before this goes in the shared repo, per the assignment's guardrails.

## Architecture notes (for the comparison table)
- **Model calls per request:** 1 (classification only)
- **Everything after classification:** plain Python, no further model involvement
- **Tradeoff:** fast and predictable, but can't reason about context the way the constrained ReAct version can (e.g. can't factor in a patient's history across messages)
