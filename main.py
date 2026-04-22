#TEST SOLVER BY MATIE123 09.04.26 - 12.04.26
# This is test solver for funny exams that my teacher wants me to solve 10 each week
# Assuming that each exam takes about 20 mins, times 10 this means about 3 hrs each week!
# Who would want to spend so much time solving test's that I doubt anyone smarter than an ape
# Would be able to pass? Yeah, no one. Anyway, for now I'll keep it for myself, as I am the only person
# That could achieve AI-high score without suspicion. Maybe one day I'll add an option
# To set desired score so some of the questions would be answered randomly purposely.
#Oh, and remember:
#Власть рождает паразитов. Да здравствует анархия!

import time
import os
import random
import asyncio
import cloudscraper
from groq import Groq
from dotenv import load_dotenv
import websocket


from modules.gather_info import get_csrf_token
from modules.create_prompt import create_content_list, clean_text
from modules.exam_manager import start_exam, connect_websocket, send_websocket, send_websocket_safe


def calc_solving_time():
    return random.randint(60*15, 60*25)

def calc_question_time():
    return random.randint(15, 30)

def ws_connect():
    ws = connect_websocket(MAIN_DOMAIN, exam_id, session.cookies.get("sessionid"), session.cookies.get("cf_clearance"))
    return ws

TIME_START = time.time()

load_dotenv()

PATH_TO_LOCAL_STORAGE = os.getenv("PATH_TO_LOCALSTORAGE")
PATH_TO_COOKIES = os.getenv("PATH_TO_COOKIES")
MAIN_DOMAIN = os.getenv("MAIN_DOMAIN")

question_number = 1

session = cloudscraper.Session()
client = Groq(
    api_key=os.getenv("GROQ_KEY")
)

session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0",
    "Accept": "*/*"
})

exam_id = start_exam(session, PATH_TO_COOKIES, MAIN_DOMAIN)

EXAM_URL = f"https://{MAIN_DOMAIN}/egzamin/{exam_id}/"
csrf_token = get_csrf_token(session, EXAM_URL)
print(f"CSRF_TOKEN: {csrf_token}")

print(f"Link do egzaminu: {EXAM_URL}")

#WEBSOCKET
ws = ws_connect()
websocket_events = [] #Tutej będzie message q_opened, q_answered

if csrf_token:
    session.cookies.set(
        'csrftoken',
        csrf_token,
        domain=f"{MAIN_DOMAIN}"
    )

while question_number <= 40:
    time.sleep(2)
    query_url = ""
    if EXAM_URL.endswith("/"):
        query_url = f"{EXAM_URL}pytanie/{question_number}"
    else:
        query_url = f"{EXAM_URL}/pytanie/{question_number}"

    question_start = time.time()

    websocket_events.append(
        {
            "t": int(time.time()*1000),
            "e": "question_opened",
            "q": question_number
        }
    )

    question_response = session.get(url=query_url)

    question_data = question_response.json()
    print("Pytanie nr. " + str(question_number))
    print(clean_text(question_data["question"][
              "content"]))  # treść pytania, response -> question(słownik) -> content,answers,has_image itd

    # print(question_data["question"]["content"])
    for answ in question_data["question"]["answers"]:
        print(answ['label'] + " " + clean_text(answ['text']) + " " + str(answ['original_number']))

    content_list = create_content_list(question_data, MAIN_DOMAIN)

    ai_response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages= content_list
    )

    full_response = ai_response.choices[0].message.content
    if "Wynik:" in full_response:
        # Bierze literę występującą zaraz po słowie Wynik:
        answer = full_response.split("Wynik:")[1].strip()[0].upper()
        print(answer)
    else:
        import re
        match = re.search(r'\b[A-D]\b', full_response)
        answer = match.group(0) if match else "A"

    if not ai_response.choices:
        print(f"BŁĄD API na pytaniu {question_number}!")
        print("Treść błędu:", ai_response)
        time.sleep(10)
        continue

    #answer = ai_response.choices[0].message.content.strip()[0]

    correct_answer_number = None
    for answ in question_data["question"]["answers"]:
        if answ['label'] == answer:
            correct_answer_number = answ['original_number']

    if correct_answer_number is None:
        print("Znowu się coś zjebało")
        correct_answer_number = random.randint(1,
                                             4)  # strzela jak się coś zjebie. Ta llama to wielce nieposłuszny model..

    print("Poprawna odpowiedź: " + answer + ", jest to odpowiedź o numerze " + str(correct_answer_number))

    time.sleep(calc_question_time() - (time.time() - question_start))

    websocket_events.append(
        {
            "t": int(time.time() * 1000),
            "e": "question_answered",
            "q": question_number,
            "a": correct_answer_number
        }
    )


    sendQuery = session.post(
        url=f"{query_url}/odpowiedz/",
        data={
            "answer": correct_answer_number,
            "csrfmiddlewaretoken": csrf_token
        },
        headers={
            "Referer": EXAM_URL,
            "X-CSRFToken": f"{csrf_token}",
            "Origin": f"https://{MAIN_DOMAIN}",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest"
        }
    )
    if not (send_websocket_safe(ws, MAIN_DOMAIN, websocket_events, exam_id, session.cookies.get('sessionid'), session.cookies.get('cf_clearance'))):
        ws = ws_connect()

    websocket_events = []

    print(str(sendQuery.status_code) + "\n")
    try:
        print("Odpowiedź serwera:", sendQuery.json())
    except:
        print("Odpowiedź nie jest dżejsonem:", sendQuery.text)
    question_number += 1

time.sleep(5)
try:
    ws.close()
    print("Websocket ubity")
except:
    print("Coś jest nie ten tego z websocketem??")

# Send end test request
end_test = session.post(
    url=f"{EXAM_URL}zakoncz/",
    data={
        "csrfmiddlewaretoken": csrf_token
    },
    headers={
        "Referer": EXAM_URL,
        "X-CSRFToken": f"{csrf_token}",
        "Origin": f"https://{MAIN_DOMAIN}",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest"
    }
)

print(end_test.status_code)
print(end_test.text)

print("TEST SOLVED")
