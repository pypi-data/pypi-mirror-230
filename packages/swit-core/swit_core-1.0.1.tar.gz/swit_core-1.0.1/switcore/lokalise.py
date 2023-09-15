import json
import os

import httpx


async def set_translate():
    localise_token: str = os.getenv('LOCALIZE_PROJECT_ID', None)

    assert localise_token is not None, "LOCALIZE_PROJECT_ID is not set check .env file"

    params = {
        "project_id": localise_token,
        "tags": "webhook proxy",
    }

    async with httpx.AsyncClient() as client:
        res = await client.get("https://ur.swit.support/get_trans", params=params, timeout=60)

    if not res.is_success:
        return res.json()

    with open("./translate.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(res.json(), indent=2))

    return res.json()


def get_translated_text(lang: str, key: str, number: str | None = None) -> str:
    with open("translate.json", "r", encoding="utf-8") as file:
        translate_info = json.load(file)

    appname: str = translate_info[lang]["webhookproxy.appname"]
    text: str = translate_info[lang][key]
    text = text.replace("{appName}", appname)
    if number:
        text = text.replace("{n}", number)
    return text
