import os
import json
import requests

from dotenv import load_dotenv

load_dotenv()

#TEST_URL = input("Please provide test URL: ")
TEST_URL = "https://zawodowe.edu.pl/egzamin/16e27edd-dcee-41de-a242-f28d10ade921/"
CSRFMIDDLEWARE_TOKEN = input("Please provide crsf middleware token: ")
question_number = 1

query_url = ""
if(TEST_URL.endswith("/")):
    query_url = f"{TEST_URL}pytanie/{question_number}"
else:
    f"{TEST_URL}/pytanie/{question_number}"

question = requests.get(
    url = query_url
)

print(question.json()["question"]["content"])

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": f"Bearer {os.getenv('API_KEY')}",
    "Content-Type": "application/json",
  },
  data=json.dumps({
    "model": "nvidia/nemotron-3-super-120b-a12b:free",
    "messages": [
        {
          "role": "user",
          "content": f"Hi! Imagine that you are professional IT test solver. Solve this question for me, but make sure that you make no mistake:"
                     f"This is the question: {question.json()['question']['content']}"
                     f"And these are the answers: {question.json()['question']['answers']}"
                     f"In the response, give me only one letter - the answer. Make sure to give the correct one."
        }
      ],
    "reasoning": {"enabled": True}
  })
)

answer = response.json()["choices"][0]["message"]["content"]
answer.strip()

correctAnswerNumber = None
for answ in question.json()["question"]["answers"]:
    if(answ['label'] == answer):
        correctAnswerNumber = answ['original_number']
# message_text = data["choices"][0]["message"]["content"]
# reasoning_text = data["choices"][0]["message"].get("reasoning", "No reasoning provided")
#
# print(f"Response: {message_text}, \n Reasoning: {reasoning_text}")
print(f"{query_url}/odpowiedz")

sendQuery = requests.post(
    url = f"{query_url}/odpowiedz/",
    data = {
        "answer": correctAnswerNumber,
        "csrfmiddlewaretoken": CSRFMIDDLEWARE_TOKEN
    },
    headers = {
        "Referer": query_url,
        "X-CSRFToken": f"{CSRFMIDDLEWARE_TOKEN}"
    }
)
#print(dir(sendQuery))
print(sendQuery.text)