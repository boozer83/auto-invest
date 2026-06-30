import json
import requests
from pathlib import Path
from config import KAKAO_REST_API_KEY

TOKEN_FILE = Path("kakao_token.json")


def _load_tokens() -> dict:
    if TOKEN_FILE.exists():
        return json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    return {}


def _save_tokens(data: dict):
    TOKEN_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _refresh_access_token() -> str:
    tokens = _load_tokens()
    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        raise RuntimeError("카카오 토큰 없음. python kakao_setup.py 를 먼저 실행하세요.")

    resp = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type":    "refresh_token",
            "client_id":     KAKAO_REST_API_KEY,
            "refresh_token": refresh_token,
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    tokens["access_token"] = data["access_token"]
    if "refresh_token" in data:
        tokens["refresh_token"] = data["refresh_token"]
    _save_tokens(tokens)
    return tokens["access_token"]


def send(text: str):
    """카카오톡 나에게 보내기"""
    access_token = _refresh_access_token()

    resp = requests.post(
        "https://kapi.kakao.com/v2/api/talk/memo/default/send",
        headers={"Authorization": f"Bearer {access_token}"},
        data={
            "template_object": json.dumps({
                "object_type": "text",
                "text":        text,
                "link":        {"web_url": "", "mobile_web_url": ""},
            }, ensure_ascii=False)
        },
        timeout=10,
    )
    resp.raise_for_status()
