import sqlite3
from bs4 import BeautifulSoup

def get_csrf_token(session, url):
    landing_page = session.get(url)
    soup = BeautifulSoup(landing_page.text, 'html.parser')
    csrf_tag = soup.find('div', {'id': 'examContainer'})

    if csrf_tag:
        token = csrf_tag['data-csrf-token']
        print("CSRF token found in div!")
        return token
    else:
        csrf_tag = soup.find('input', {'name': 'csrfmiddlewaretoken'})

        if csrf_tag:
            token = csrf_tag['value']
            print("CSRF token found in input!")
            return token
        else:
            return input(
                "CSRF token not found! Please provide csrf middleware token: ")

def get_exam_id(path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("SELECT key FROM data WHERE key LIKE 'exam%' ORDER BY rowid DESC LIMIT 1")
    key = cursor.fetchall()[-1]
    conn.close()
    print(str(key[0]).removesuffix("_questions").removeprefix("exam_")) #For debug reasons
    return str(key[0]).removesuffix("_questions").removeprefix("exam_")

def get_session_id(path, domain):
    """

    :param path: path to browser cookies
    :param domain: domain of site
    :return: session id
    """
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT value FROM moz_cookies WHERE host LIKE '{domain}' AND name LIKE 'sessionid'")
    key = cursor.fetchone()
    conn.close()
    return str(key[0])
def get_cf_clearance(path, domain):
    """

    :param path: path to browser cookies
    :param domain: domain of site
    :return: cf clearance (possibly not needed)
    """
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT value FROM moz_cookies WHERE host LIKE '.{domain}' AND name LIKE 'cf_clearance'")
    key = cursor.fetchone()
    conn.close()
    return str(key[0])
