"""
Plain, testable functions the agent is allowed to call.
This IS the allow-list implementation -- agent.py only imports from here,
nothing else is ever exposed to the model.
"""

import json
import random as rand
import os

import os

BASE_DIR = os.path.dirname(__file__)

with open(os.path.join(BASE_DIR, "doctors.json"), "r") as f:
    doctors = json.load(f)

ROUTE_MAP = {
    "BURNS": "go to burns department quickly",
    "DIABETES": "you may have diabetes, go to blood measurement department",
    "ORTHOPEDIC": "you should go to the bone department",
    "OPHTHALMOLOGY": "You should visit the ophthalmology department.",
    "CARDIOLOGY": "go to the cardiology department immediately",
    "TOXICOLOGY": "go to the toxicology / poison control department",
    "TRAUMA": "go to the trauma / emergency room immediately",
    "NEUROLOGY": "go to the neurology department",
    "ALLERGY": "go to the allergy and immunology department",
    "MATERNITY": "go to the maternity department immediately",
    "GASTROENTEROLOGY": "go to the gastroenterology department",
    "GENERAL_MEDICINE": "go to the general medicine department",
    "DERMATOLOGY": "go to the dermatology / wound care department",
}


def _normalize(name: str) -> str:
    name = name.strip()
    if not name.lower().startswith("dr"):
        name = "Dr " + name
    return name.title()


def check_doctor_availability(doctor_name: str) -> str:
    """Simulates a live availability check for a doctor."""
    doctor_name = _normalize(doctor_name)
    if doctor_name not in doctors:
        return f"Unknown doctor: {doctor_name}"
    available = rand.choice([True, False])
    return f"{doctor_name} is {'available' if available else 'not available'}"


def get_doctor_schedule(doctor_name: str) -> str:
    doctor_name = _normalize(doctor_name)
    if doctor_name not in doctors:
        return f"Unknown doctor: {doctor_name}"
    return f"{doctor_name} working hours: {doctors[doctor_name]}"


def list_all_doctors() -> str:
    lines = [f"{name} -> {hours}" for name, hours in doctors.items()]
    return "\n".join(lines)


def route_department(symptom_category: str) -> str:
    symptom_category = symptom_category.upper().strip()
    return ROUTE_MAP.get(symptom_category, f"Unknown category: {symptom_category}")
