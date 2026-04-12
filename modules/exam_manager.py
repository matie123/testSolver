import cloudscraper

from modules.gather_info import get_session_id, get_csrf_token, get_cf_clearance

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
