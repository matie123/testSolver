import os
import json
import requests
import cloudscraper
import time
from groq import Groq
import random
from bs4 import BeautifulSoup
import sqlite3
from dotenv import load_dotenv

load_dotenv()


def get_exam_id():
    conn = sqlite3.connect(os.getenv("PATH_TO_LOCALSTORAGE"))
    cursor = conn.cursor()
    cursor.execute("SELECT key FROM data WHERE key LIKE 'exam%' LIMIT 1")
    key = cursor.fetchone()
    conn.close()
    return str(key[0]).removesuffix("_questions").removeprefix("exam_")

def get_session_id():
    conn = sqlite3.connect(os.getenv("PATH_TO_COOKIES"))
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM moz_cookies WHERE host LIKE 'zawodowe.edu.pl' AND name LIKE 'sessionid'")
    key = cursor.fetchone()
    conn.close()
    return str(key[0])

print(get_exam_id())
print(type(get_exam_id()))
print(get_session_id())