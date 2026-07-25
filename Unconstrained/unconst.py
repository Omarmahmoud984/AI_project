import os
import json
import random as rand
from google import genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
client = genai.Client(api_key=API_KEY)

with open("doctors.json", "r") as f:
    doctors = json.load(f)

def get_availability(doctors_dict):
    # same mocked random availability as the reactive/routing agents
    return {name: rand.choice([True, False]) for name in doctors_dict}

SYSTEM_PROMPT = """You are a hospital triage chat assistant. Talk to the patient naturally,
reason about their symptoms, and tell them where to go. If they ask about a doctor,
use the doctor info and availability given below use the availabilty from the below data don't use real time . Decide freely how to respond —
no fixed rules, no format required.
 **BUT** don't write alot of text just a summary you are a quick helping bot 
 """

print("Hi! How can I help you today?")

history = ""
availability = get_availability(doctors)  # rolled once per session, like your other agents

while True:
    user_inp = input("You: ")
    if user_inp.lower() == "quit":
        break

    history += f"\nPatient: {user_inp}"
    doctor_context = {
        name: {"hours": hours, "available": availability[name]}
        for name, hours in doctors.items()
    }
    prompt = f"{SYSTEM_PROMPT}\n\nDoctor info: {json.dumps(doctor_context)}\n\nConversation so far:{history}\nAssistant:"

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    reply = response.text.strip()
    print(f"Bot: {reply}")
    history += f"\nAssistant: {reply}"