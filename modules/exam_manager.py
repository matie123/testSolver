import json
import random
import ssl
import time

import cloudscraper
from modules.gather_info import get_session_id, get_csrf_token, get_cf_clearance
import websocket

_sequence_counter = 1

def start_exam(session: cloudscraper.Session, path, domain):
    """
    :param session: active cloudscraper session
    :param path: path to browser cookies
    :param domain: main domain
    :return: exam id
    """
    session_id = get_session_id(path, domain)
    cf_clearance = get_cf_clearance(path, domain)


    print(f"SESSION_ID: {session_id}")
    print(f"CF_CLEARANCE: {cf_clearance}")

    session.cookies.set(
        'sessionid',
        session_id,
        domain=f"{domain}"
    )

    session.cookies.set(
        'cf_clearance',
        cf_clearance,
        domain=f".{domain}"
    )

    csrf_token = get_csrf_token(session, f"https://{domain}/egzamin/")
    print(f"CSRF_TOKEN: {csrf_token}")

    request = session.post(
        url=f"https://{domain}/egzamin/utworz/technik-programista/inf-03/",
        data={
            "csrfmiddlewaretoken": f"{csrf_token}",
            "official_mode": "false",
            "categories[]": [
                '557', '558', '559', '560', '561', '562', '563', '831', '839'
            ]
        },
        headers = {
            "Referer": f"https://{domain}/egzamin/?profession=technik-programista&qualification=inf-03",
            "X-CSRFToken": f"{csrf_token}",
            "Origin": f"https://{domain}",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest"
        }
    )

    return request.json()["exam_id"]

def connect_websocket(domain, exam_id, session_id, cf_clearance):
    ws_url = f"wss://{domain}/ws/exam/{exam_id}/"

    print(f"Oto websocket url: {ws_url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:150.0) Gecko/20100101 Firefox/150.0",
        "Origin": f"https://{domain}",
        "Cookie": f"sessionid={session_id}; cf_clearance={cf_clearance}"
    }

    ws = websocket.create_connection(ws_url, header=headers, ping_interval=60)
    return ws

def send_websocket(ws, data):
    global _sequence_counter

    message = {
        "type": "events",
        "seq": _sequence_counter,
        "events": data
    }

    ws.send(json.dumps(message))
    _sequence_counter+=1

def send_websocket_safe(ws, domain, data, exam_id, session_id, cf_clearance):
    try:
        send_websocket(ws, data)
        return True
    except (websocket.WebSocketConnectionClosedException, ssl.SSLEOFError, ConnectionAbortedError):
        print("Połączenie przerwane. Próbuję połączyć ponownie...")
        return False

# RANDOM FOCUS LOST
def random_focus_lost(websocket_events: list):
    if(random.randint(1, 30) == 1):
        websocket_events.append(
            {
                "t": int(time.time() * 1000),
                "e": "focus_lost"
            }
        )
        wait_time = random.randint(2000, 14000) #In millis
        time.sleep(int(wait_time/1000))
        websocket_events.append(
            {
                "t": int(time.time() * 1000)+wait_time,
                "e": "focus_regained",
                "away": wait_time
            }
        )
    return websocket_events

# RANDOM QUESTION OPEN
def random_question_open(websocket_events: list):
    pass #todo