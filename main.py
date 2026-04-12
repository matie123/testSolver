#TEST SOLVER BY MATIE123 09.04.26 - 12.04.26
#This is test solver for funny exams that my teacher wants me to solve 10 each week
#Assuming that each exam takes about 30 mins, times 10 this means about 5 hrs each week!
#Who would want to spend so much time solving test's that i doubt anyone smarter than an ape
#Would be able to pass? Yeah, no one. Anyway, for now I'll keep it for myself, as I am the only person
#That could achieve AI-high score without teacher's suspicion. Maybe one day I'll add an option
#To set desired score so some of the questions would be answered randomly purposely.
#Oh and remember:
#Власть рождает паразитов. Да здравствует анархия!

import os
import json
import requests
import cloudscraper
import time
from Tools.demo.spreadsheet import cellname
from groq import Groq
import random
from bs4 import BeautifulSoup
import sqlite3
from dotenv import load_dotenv
import html

SYSTEM_MESSAGE = (
    "Jesteś wybitnym ekspertem IT, specjalizującym się w polskich egzaminach zawodowych "
    "(INF.02, INF.03, E.12, E.14). Twoim zadaniem jest bezbłędne rozwiązywanie testów. "
    "Zawsze analizuj każde pytanie krok po kroku, eliminując błędne odpowiedzi."
)

def clean_text(text):
    if not text:
        return ""
    text = html.unescape(html.unescape(text))
    text = text.replace('”', '"').replace('„', '"').replace('’', "'")
    text = text.replace('\xa0', ' ')
    return text.strip()

def create_content_list(question_data):
    raw_content = question_data['question']['content']
    clean_content = clean_text(raw_content)

    clean_answers = []
    for answ in question_data["question"]["answers"]:
        clean_answers.append(
            {
                "label": answ["label"],
                "text": clean_text(answ["text"])
            }
        )

    content_list = [
        {
            "type": "text",
            "text": f"PRZEANALIZUJ PYTANIE I WYBIERZ POPRAWNĄ ODPOWIEDŹ.\n\n"
                    f"Pytanie: {clean_content}\n"
                    f"Odpowiedzi:\n{clean_answers}\n\n"
                    "INSTRUKCJA:\n"
                    "1. W sekcji 'Analiza:' krótko uzasadnij wybór.\n"
                    "2. W sekcji 'Wynik:' podaj tylko i wyłącznie jedną literę (A, B, C lub D).\n"
                    "Pamiętaj: Jeśli pytanie dotyczy grafiki, lub filmu którego nie widzisz, opieraj się na tekście, w ostateczności wylosuj odpowiedź."
        }
    ]

    if question_data["question"]["has_images"]:
        content_list.append(
            {
                "type": "image_url",
                "image_url": {"url": f"https://zawodowe.edu.pl{question_data['question']['image']}"}
            }
        )
    return content_list


def get_exam_id():
    conn = sqlite3.connect(os.getenv("PATH_TO_LOCALSTORAGE"))
    cursor = conn.cursor()
    cursor.execute("SELECT key FROM data WHERE key LIKE 'exam%'")
    key = cursor.fetchall()[-1]
    conn.close()
    print(str(key[0]).removesuffix("_questions").removeprefix("exam_")) #For debug reasons
    return str(key[0]).removesuffix("_questions").removeprefix("exam_")


def get_session_id():
    conn = sqlite3.connect(os.getenv("PATH_TO_COOKIES"))
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM moz_cookies WHERE host LIKE 'zawodowe.edu.pl' AND name LIKE 'sessionid'")
    key = cursor.fetchone()
    conn.close()
    return str(key[0])


def get_csrf_token(session):
    landing_page = session.get(TEST_URL)
    soup = BeautifulSoup(landing_page.text, 'html.parser')
    csrf_tag = soup.find('div', {'id': 'examContainer'})

    if (csrf_tag):
        token = csrf_tag['data-csrf-token']
        print("CSRF token found!")
        return token
    else:
        return input(
            "Token not found!: Please provide crsf middleware token: ")  # Jeśli to się odpala to prawdopodobnie data token jest inny aniżeli ten drugi


load_dotenv()

# TEST_URL = input("Please provide test URL: ")
TEST_URL = f"https://zawodowe.edu.pl/egzamin/{get_exam_id()}/"
# CSRFMIDDLEWARE_TOKEN = input("Please provide crsf middleware token: ")
SESSION_ID = get_session_id()

question_number = 1

session = cloudscraper.Session()
client = Groq(
    api_key=os.getenv("GROQ_KEY")
)

session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0",
    "Accept": "*/*"
})


session.cookies.set(
    'sessionid',
    SESSION_ID,
    domain="zawodowe.edu.pl"
)

CSRFMIDDLEWARE_TOKEN = get_csrf_token(session)

if(CSRFMIDDLEWARE_TOKEN):
    session.cookies.set(
        'csrftoken',
        CSRFMIDDLEWARE_TOKEN,
        domain="zawodowe.edu.pl"
    )

while question_number <= 40:
    time.sleep(2)
    query_url = ""
    if (TEST_URL.endswith("/")):
        query_url = f"{TEST_URL}pytanie/{question_number}"
    else:
        query_url = f"{TEST_URL}/pytanie/{question_number}"

    question_response = session.get(url=query_url)

    question_data = question_response.json()
    print("Pytanie nr. " + str(question_number))
    print(clean_text(question_data["question"][
              "content"]))  # treść pytania, response -> question(słownik) -> content,answers,has_image itd

    # print(question_data["question"]["content"])
    for answ in question_data["question"]["answers"]:
        print(answ['label'] + " " + clean_text(answ['text']) + " " + str(answ['original_number']))

    content_list = create_content_list(question_data)

    ai_response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role" : "system",
                "content": SYSTEM_MESSAGE
            },
            {
                "role": "user",
                "content": content_list
            }
        ]
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

    correctAnswerNumber = None
    for answ in question_data["question"]["answers"]:
        if (answ['label'] == answer):
            correctAnswerNumber = answ['original_number']

    if (correctAnswerNumber is None):
        print("Znowu się coś zjebało")
        correctAnswerNumber = random.randint(1,
                                             4)  # strzela jak się coś zjebie. Ta llama to wielce nieposłuszny model..

    print("Poprawna odpowiedź: " + answer + ", jest to odpowiedź o numerze " + str(correctAnswerNumber))

    sendQuery = session.post(
        url=f"{query_url}/odpowiedz/",
        data={
            "answer": correctAnswerNumber,
            "csrfmiddlewaretoken": CSRFMIDDLEWARE_TOKEN
        },
        headers={
            "Referer": TEST_URL,
            "X-CSRFToken": f"{CSRFMIDDLEWARE_TOKEN}",
            "Origin": "https://zawodowe.edu.pl",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest"
        }
    )
    # print(dir(sendQuery))
    print(str(session.headers) + "\n")
    print(str(session.cookies) + "\n")
    print(str(sendQuery.status_code) + "\n")
    try:
        print("Odpowiedź serwera:", sendQuery.json())
    except:
        print("Odpowiedź nie jest dżejsonem:", sendQuery.text)
    question_number += 1;
    if (question_number % 20 == 0):
        time.sleep(60)

# Send end test request
end_test = session.post(
    url=f"{TEST_URL}zakoncz/",
    data={
        "csrfmiddlewaretoken": CSRFMIDDLEWARE_TOKEN
    },
    headers={
        "Referer": TEST_URL,
        "X-CSRFToken": f"{CSRFMIDDLEWARE_TOKEN}",
        "Origin": "https://zawodowe.edu.pl",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest"
    }
)

print(end_test.status_code)
print(end_test.text)

print("TEST SOLVED")
