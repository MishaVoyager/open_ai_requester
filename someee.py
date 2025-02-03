import json

import requests


def get_search_result(prompt: str) -> dict:
    body = {
        "prompt": prompt,
        "source": "YANDEX",
        "model": "gpt-4o-mini"
    }
    data = json.dumps(body)
    response = requests.post(url="http://185.245.107.252:7999/search", data=data)
    return response.json()


result = get_search_result("Насколько большая галерея Уфицци? Расскажи про нее")
answer = result["answer"]
is_refusal = result["is_refusal"]
is_success = result["is_success"]
print()
