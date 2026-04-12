import os
import cloudscraper
import time
from groq import Groq
import random

from modules.gather_info import *

from dotenv import load_dotenv

load_dotenv()

PATH_TO_LOCAL_STORAGE = os.getenv("PATH_TO_LOCALSTORAGE")
PATH_TO_COOKIES = os.getenv("PATH_TO_COOKIES")
MAIN_DOMAIN = os.getenv("MAIN_DOMAIN")

def start_test(session: cloudscraper.Session):
    session_id = get_session_id(PATH_TO_COOKIES, MAIN_DOMAIN)
    cf_clearance = get_cf_clearance(PATH_TO_COOKIES, MAIN_DOMAIN)


    print(f"SESSION_ID: {session_id}")
    print(f"CF_CLEARANCE: {cf_clearance}")

    session.cookies.set(
        'sessionid',
        session_id,
        domain=f"{MAIN_DOMAIN}"
    )

    session.cookies.set(
        'cf_clearance',
        cf_clearance,
        domain=f".{MAIN_DOMAIN}"
    )

    csrf_token = get_csrf_token(session, f"https://{MAIN_DOMAIN}/egzamin/")
    print(f"CSRF_TOKEN: {csrf_token}")

    request = session.post(
        url=f"https://{MAIN_DOMAIN}/egzamin/utworz/technik-programista/inf-03/",
        data={
            "csrfmiddlewaretoken": f"{csrf_token}",
            "official_mode": "false",
            "categories[]": [
                '557', '558', '559', '560', '561', '562', '563', '831', '839'
            ]
        },
        headers = {
            "Referer": f"https://{MAIN_DOMAIN}/egzamin/?profession=technik-programista&qualification=inf-03",
            "X-CSRFToken": f"{csrf_token}",
            "Origin": f"https://{MAIN_DOMAIN}",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest"
        }
    )

    return request.json()["exam_id"]

session = cloudscraper.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:149.0) Gecko/20100101 Firefox/149.0",
    "Accept": "*/*"
})

exam_id = start_test(session)
exam_url = f"https://{MAIN_DOMAIN}/egzamin/{exam_id}/"

