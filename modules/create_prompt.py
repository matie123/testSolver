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

def create_content_list(question_data, domain):
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
                "image_url": {"url": f"https://{domain}{question_data['question']['image']}"}
            }
        )
    return [
        {
            "role": "system",
            "content": SYSTEM_MESSAGE
        },
        {
            "role": "user",
            "content": content_list
        }
    ]