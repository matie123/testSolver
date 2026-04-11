import os
import json
import requests
import cloudscraper
import time
from groq import Groq
import random

from dotenv import load_dotenv

load_dotenv()

#TEST_URL = input("Please provide test URL: ")
TEST_URL = "https://zawodowe.edu.pl/egzamin/d22c0b21-00fd-44b4-8042-4d2d084f033a/"
CSRFMIDDLEWARE_TOKEN = input("Please provide crsf middleware token: ")
SESSION_ID = input("Please provide session id: ")

question_number = 1

session = cloudscraper.Session()
client = Groq(
    api_key = os.getenv("GROQ_KEY")
)

session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0",
    "Accept": "*/*"
})

session.cookies.set(
    'csrftoken',
    CSRFMIDDLEWARE_TOKEN,
    domain = "zawodowe.edu.pl"
)
session.cookies.set(
    'sessionid',
    SESSION_ID,
    domain = "zawodowe.edu.pl"
)
# session.cookies.set(
#     'cf_clearance',
#     CF_CLEARANCE,
#     domain = "zawodowe.edu.pl"
# )

while question_number <= 40:
    time.sleep(2)
    query_url = ""
    if(TEST_URL.endswith("/")):
        query_url = f"{TEST_URL}pytanie/{question_number}"
    else:
        query_url = f"{TEST_URL}/pytanie/{question_number}"

    question_response = session.get(url = query_url)
    question_data = question_response.json()
    print(question_data)

    #print(question_data["question"]["content"])
    for answ in question_data["question"]["answers"]:
        print(answ['label'] + " " + answ['text'] + " " + str(answ['original_number']))

    # ai_response = requests.post(
    #   url="https://openrouter.ai/api/v1/chat/completions",
    #   headers={
    #     "Authorization": f"Bearer {os.getenv('API_KEY')}",
    #     "Content-Type": "application/json",
    #   },
    #   data=json.dumps({
    #     "model": "nvidia/nemotron-3-super-120b-a12b:free",
    #     "messages": [
    #         {
    #           "role": "user",
    #           "content": f"Hi! Imagine that you are professional IT test solver. Solve this question for me, but make sure that you make no mistake:"
    #                      f"This is the question: {question_data['question']['content']}"
    #                      f"And these are the answers: {question_data['question']['answers']}"
    #                      f"In the response, give me only one letter - the answer. Make sure to give the correct one."
    #         }
    #       ],
    #     "reasoning": {"enabled": True}
    #   })
    # )

    content_list = [
                    {
                        "type": "text",
                        "text": f"Hi! Imagine that you are professional IT test solver. Solve this question for me, but make sure that you make no mistake:"
                           f"This is the question: {question_data['question']['content']}"
                           f"And these are the answers: {question_data['question']['answers']}"
                           f"In the response, give me only one letter - the answer. Make sure to give the correct one."
                           f"If you don't have enough information - for example the question mentions a video, but "
                           f"you don't see one, give random answer. RESPONSE ONLY WITH ONE CHARACTER - THE CORRECT ANSWER LETTER, WITHOUT ANYTHING ELSE, EVEN WITHOUT A DOT!!!!"
                    }
                    #if has_images then add image to request
    ]

    if question_data["question"]["has_images"]:
        content_list.append(
            {
                "type": "image_url",
                "image_url": { "url": f"https://zawodowe.edu.pl{question_data['question']['image']}" }
            }
        )

    print(content_list)

    ai_response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": content_list
            }
        ]
    )


    if not ai_response.choices:
        print(f"BŁĄD API na pytaniu {question_number}!")
        print("Treść błędu:", ai_response)
        time.sleep(10)
        continue

    answer = ai_response.choices[0].message.content.strip()[0]

    correctAnswerNumber = None
    for answ in question_data["question"]["answers"]:
        if(answ['label'] == answer):
            correctAnswerNumber = answ['original_number']

    if(correctAnswerNumber is None):
        print("Znowu się coś zjebało")
        correctAnswerNumber = random.randint(1, 4) #strzela jak się coś zjebie. Ta llama to wielce nieposłuszny model..


    print("Poprawna odpowiedź: " + answer + ", jest to odpowiedź o numerze " + str(correctAnswerNumber))

    sendQuery = session.post(
        url = f"{query_url}/odpowiedz/",
        data = {
            "answer": correctAnswerNumber,
            "csrfmiddlewaretoken": CSRFMIDDLEWARE_TOKEN
        },
        headers = {
            "Referer": TEST_URL,
            "X-CSRFToken": f"{CSRFMIDDLEWARE_TOKEN}",
            "Origin": "https://zawodowe.edu.pl",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest"
        }
    )
    #print(dir(sendQuery))
    print(str(session.headers) + "\n")
    print(str(session.cookies) + "\n")
    print(str(sendQuery.status_code) + "\n")
    try:
        print("Odpowiedź serwera:", sendQuery.json())
    except:
        print("Odpowiedź nie jest dżejsonem:", sendQuery.text)
    question_number+=1;
    if(question_number % 20 == 0 ):
        time.sleep(60)

print("TEST SOLVED")