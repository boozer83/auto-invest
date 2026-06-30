import time
import requests
from config import APP_KEY, APP_SECRET, BASE_URL

_token: str = ""
_token_expires: float = 0.0


def get_token() -> str:
    global _token, _token_expires

    if _token and time.time() < _token_expires:
        return _token

    resp = requests.post(
        f"{BASE_URL}/oauth2/tokenP",
        headers={"Content-Type": "application/json"},
        json={
            "grant_type": "client_credentials",
            "appkey":     APP_KEY,
            "appsecret":  APP_SECRET,
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    _token = data["access_token"]
    # 토큰 만료 1분 전에 갱신
    _token_expires = time.time() + int(data.get("expires_in", 86400)) - 60
    return _token


def auth_headers(tr_id: str) -> dict:
    return {
        "Content-Type":  "application/json; charset=utf-8",
        "authorization": f"Bearer {get_token()}",
        "appkey":        APP_KEY,
        "appsecret":     APP_SECRET,
        "tr_id":         tr_id,
        "custtype":      "P",
    }
