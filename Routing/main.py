from google import genai
import json 
import random as rand
with open ('doctors.json' , 'r') as f :
    doctors = json.load(f)

def get_dr_stat(text) :
    av = rand.choice([True,False])
    if av : 
        return(f'{text} is available')
    else :
        return(f'{text} isn\'t available')


def display_all_DRs(file :dict) : 
    result = '=' * 40 + '\n'
    for key , val in file.items() :
         result += f'{key} working time is {val}\n'
    result += '=' * 40
    return result
        


# ---------- Setup ----------
API_KEY = ''
client = genai.Client(api_key=API_KEY)
print('Hi!\nhow can i assist you today?')
CATEGORIES = [
    "BURNS", "DIABETES", "ORTHOPEDIC", "OPHTHALMOLOGY", "CARDIOLOGY",
    "TOXICOLOGY", "TRAUMA", "NEUROLOGY", "ALLERGY", "MATERNITY",
    "GASTROENTEROLOGY", "GENERAL_MEDICINE", "DERMATOLOGY",
    "DOCTOR_INFO", "GREETING", "THANKS", "GOODBYE", "UNKNOWN"
]

ROUTING_PROMPT = """You are a strict classifier for a hospital triage system. 
Read the patient's message and classify it into EXACTLY ONE of these categories and focus before classification:

BURNS, DIABETES, ORTHOPEDIC, OPHTHALMOLOGY, CARDIOLOGY, TOXICOLOGY, 
TRAUMA, NEUROLOGY, ALLERGY, MATERNITY, GASTROENTEROLOGY, 
GENERAL_MEDICINE, DERMATOLOGY, DOCTOR_INFO, GREETING, THANKS, 
GOODBYE, UNKNOWN

Rules:
- Pick the single most urgent/relevant category if multiple symptoms are mentioned.
- If the message explicitly denies or negates a symptom (e.g. "I don't have X", "my X is fine"), do NOT classify it under that symptom's category. Classify as GENERAL_MEDICINE or UNKNOWN instead.
- If the message asks about a specific doctor or wants doctor info, use DOCTOR_INFO.
- If nothing matches clearly, use UNKNOWN.
- small hint these are the doctors names to classify well -> [Ahmed, Sara, Mohamed, Nour, Yasmine]

Respond with ONLY the category name, nothing else. No explanation, no punctuation.

Patient message: "{}"
"""

# ---------- Model call (the ONLY model call in this architecture) 
def classify(user_input: str) -> str:
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=ROUTING_PROMPT.format(user_input)
    )
    return response.text.strip()

# ---------- Everything below is plain, hardcoded, testable code 
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
    "GREETING": "hi! how can I assist you today",
    "THANKS": "No problem!",
}

def handle_message(user_input: str) -> str:
    category = classify(user_input)

    if category == "GOODBYE":
        return "Happy to help! good bye"

    elif category == "DOCTOR_INFO":
            if  'ahmed' in user_input and "n't" not in user_input :
                  print(f'the doctor working time is {doctors["Dr Ahmed"]}')

                  return get_dr_stat('Dr Ahmed')
            elif  'sara' in user_input :

                  print(f'the doctor working time is {doctors["Dr Sara"]}')
                  return get_dr_stat('Dr Sara')

            elif  'moham' in user_input :
                  print(f'the doctor working time is {doctors["Dr Mohamed"]}')

                  return get_dr_stat('Dr Mohamed')
            elif  'nour' in user_input :

                  print(f'the doctor working time is {doctors["Dr Nour"]}')
                  return get_dr_stat('Dr Nour')

            elif  'yasmi' in user_input :
                  print(f'the doctor working time is {doctors["Dr Yasmine"]}')
                  return get_dr_stat('Dr Yasmine')

            else :

                return display_all_DRs(doctors)


    elif category in ROUTE_MAP:
            return ROUTE_MAP[category]

    else:
        return "sorry i don't understand your request"


# ---------- Test loop ----------
while True:
    try :
        user_inp = input().lower()
        if user_inp == "quit":
            break
        print(handle_message(user_inp)) 
    except Exception as e:
         print(f'error -> {e}')
         print('send again later')