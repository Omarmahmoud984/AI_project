"""
Constrained ReAct Agent -- Hospital Emergency Triage System
=============================================================
Same reasoning loop as the unconstrained ReAct version, but:
  - every step must match the AgentStep schema  (schema.py)
  - tool calls are restricted to TOOL_ALLOWLIST  (below)
  - a MAX_STEPS budget is enforced               (below)
  - the loop must end in final_answer OR escalate=True

Run:  python agent.py
Needs: a .env file with GEMINI_API_KEY=... (see .env.example)
Model: gemini-3.5-flash-lite (Google AI Studio free tier)
"""
import time
import os
import json
from dotenv import load_dotenv
from google import genai
from pydantic import ValidationError
from tenacity import retry, stop_after_attempt, wait_fixed

from schema import AgentStep
from tools import (
    check_doctor_availability,
    get_doctor_schedule,
    list_all_doctors,
    route_department,
)

# ---------------------------------------------------------------------------
# CONSTRAINTS -- kept visible on purpose, not buried in the loop below
# ---------------------------------------------------------------------------
MAX_STEPS = 6

TOOL_ALLOWLIST = {
    "check_doctor_availability": check_doctor_availability,
    "get_doctor_schedule": get_doctor_schedule,
    "list_all_doctors": list_all_doctors,
    "route_department": route_department,
}
# ---------------------------------------------------------------------------

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY not found. Copy .env.example to .env and put your "
        "key there. Never commit the real key."
    )

client = genai.Client(api_key=API_KEY)
MODEL = "gemini-3.5-flash-lite"

SYSTEM_PROMPT = """You are a constrained hospital triage ReAct agent.

You must respond with ONLY a single JSON object, matching exactly this shape:
{{
  "thought": "<your reasoning for this step>",
  "action": {{"tool": "<tool_name>", "args": {{...}}}} or null,
  "final_answer": "<message to give the patient>" or null,
  "escalate": true or false
}}

Rules:
- Call AT MOST one tool per step.
- Eventually you must either set "final_answer" (case resolved) or
  "escalate": true (you cannot safely resolve this, a human takes over).
- Never set both "action" and "final_answer" in the same step.
- Never invent a tool outside the allow-list below.
- No text outside the JSON object. No markdown fences.

Available tools:
- check_doctor_availability(doctor_name: str)
- get_doctor_schedule(doctor_name: str)
- list_all_doctors()
- route_department(symptom_category: str)
  valid categories: BURNS, DIABETES, ORTHOPEDIC, OPHTHALMOLOGY, CARDIOLOGY,
  TOXICOLOGY, TRAUMA, NEUROLOGY, ALLERGY, MATERNITY, GASTROENTEROLOGY,
  GENERAL_MEDICINE, DERMATOLOGY

Conversation so far:
{history}

Patient message: "{user_input}"

Respond with the JSON object for your NEXT step only.
"""


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def call_model(prompt: str) -> AgentStep:
    """Calls the model and validates its response against AgentStep.
    Retries (tenacity) up to 3x if the model returns bad JSON / bad schema."""
    response = client.models.generate_content(model=MODEL, contents=prompt)
    raw = response.text.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data = json.loads(raw)          # bad JSON -> raises -> retry
    return AgentStep(**data)        # bad schema -> raises -> retry


def run_agent(user_input: str) -> str:
    history = []

    for step_num in range(1, MAX_STEPS + 1):
        prompt = SYSTEM_PROMPT.format(
            history="\n".join(history) if history else "(none yet)",
            user_input=user_input,
        )

        try:
            step = call_model(prompt)
        except (ValidationError, json.JSONDecodeError) as e:
            return f"[ESCALATED] Agent failed to produce a valid step ({e}). A human must review this case."

        history.append(f"Step {step_num} thought: {step.thought}")

        if step.escalate:
            return "[ESCALATED] " + (step.final_answer or "This case needs a human's judgment.")

        if step.final_answer:
            return step.final_answer

        if step.action:
            if step.action.tool not in TOOL_ALLOWLIST:
                return f"[ESCALATED] Model requested a tool outside the allow-list: {step.action.tool}"
            tool_fn = TOOL_ALLOWLIST[step.action.tool]
            try:
                observation = tool_fn(**step.action.args)
            except TypeError as e:
                return f"[ESCALATED] Tool call failed validation: {e}"
            history.append(f"Step {step_num} observation: {observation}")
        else:
            return "[ESCALATED] Agent produced an empty step (no action, no final answer)."

    return "[ESCALATED] MAX_STEPS budget exceeded without a resolved answer."


if __name__ == "__main__":
    print("Hi! I'm the Hospital constrained-ReAct triage assistant. (type 'quit' to exit)")
    while True:
        user_inp = input("> ")
        
        if user_inp.lower() == "quit":
            break
        
        start = time.perf_counter()

        result = run_agent(user_inp)

        end = time.perf_counter()

        print(result)
        
        print(f"TOTAL Response Time: {end - start:.4f} seconds")
