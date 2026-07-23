# start of hard coded part plan is to make emergency Hospital system and inforamtion systen about the doctors 
import json
import random as rand

with open("doctors.json", "r") as file:
    doctors = json.load(file)

def display_all_DRs(file :dict) : 
    print('=' * 40)
    for key , val in file.items() :
        print(key ,'working time -> ' , val)
    print('=' * 40)




print("Hi!\nAm Hospital Chat system Any help !")

def get_dr_stat(text) :
    av = rand.choice([True,False])
    if av : 
        print(f'{text} is available')
    else :
        print(f'{text} isn\'t available')





while True :
    user_inp = input().lower()
    if ('fire' in user_inp or 'burn' in user_inp) and 'doctor' not in user_inp:
        print('go to burns department quickly')

    elif 'sugar' in user_inp : 
        print('you may have diabtes go to blood measurement department')

    elif 'bone' in user_inp : 
        print('you should go to the bone department')

    elif 'eye' in user_inp :
        print('You should visit the ophthalmology department.')

    elif 'chest' in user_inp or 'heart' in user_inp :
        print('go to the cardiology department immediately')

    elif 'breath' in user_inp or 'chok' in user_inp :
        print('go to the emergency room right now')

    elif 'poison' in user_inp or 'swallow' in user_inp :
        print('go to the toxicology / poison control department')

    elif 'bleed' in user_inp or 'blood loss' in user_inp :
        print('go to the trauma / emergency room immediately')

    elif 'head' in user_inp and 'ache' not in user_inp :
        print('go to the neurology department for head injuries')

    elif 'faint' in user_inp or 'dizzy' in user_inp or 'unconscious' in user_inp :
        print('go to the emergency room immediately')

    elif 'seizure' in user_inp or 'fit' in user_inp :
        print('go to the neurology / emergency department')

    elif 'allerg' in user_inp or 'rash' in user_inp :
        print('go to the allergy and immunology department')

    elif 'pregnan' in user_inp or 'labor' in user_inp :
        print('go to the maternity department immediately')

    elif 'stomach' in user_inp or 'belly' in user_inp :
        print('go to the gastroenterology department')

    elif 'fever' in user_inp or 'temperature' in user_inp :
        print('go to the general medicine department')

    elif 'pressure' in user_inp or 'hypertension' in user_inp :
        print('go to the cardiology department')

    elif 'skin' in user_inp or 'wound' in user_inp :
        print('go to the dermatology / wound care department')

    elif  'ahmed' in user_inp :
        print(f'the doctor working time is {doctors["Dr Ahmed"]}')

        get_dr_stat('Dr Ahmed')
    elif  'sara' in user_inp :

        print(f'the doctor working time is {doctors["Dr Sara"]}')
        get_dr_stat('Dr Sara')

    elif  'moham' in user_inp :
        print(f'the doctor working time is {doctors["Dr Mohamed"]}')

        get_dr_stat('Dr Mohamed')
    elif  'nour' in user_inp :

        print(f'the doctor working time is {doctors["Dr Nour"]}')
        get_dr_stat('Dr Nour')

    elif  'yasmine' in user_inp :
        print(f'the doctor working time is {doctors["Dr Yasmine"]}')
        get_dr_stat('Dr Yasmine')

    elif 'bye' in user_inp :
        print('Happy to help! you\ngood bye')
        break
    
    elif 'dr' in user_inp or 'doctor' in user_inp :

        display_all_DRs(doctors)
    elif 'hi' in user_inp :

        print('hi! how i can assist you today')
    elif 'thx' in user_inp or 'thank' in user_inp or 'ty' in user_inp :
        print('No Problem!')

    else :
        print('sorry i don\'t understand your request')

    



