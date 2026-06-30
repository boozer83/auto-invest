"""
카카오톡 최초 인증 스크립트 (최초 1회만 실행)

사전 준비:
1. https://developers.kakao.com → 내 애플리케이션 → 앱 추가
2. 앱 설정 → 카카오 로그인 → 활성화 ON
3. 카카오 로그인 → Redirect URI 추가: https://example.com
4. 동의항목 → 카카오톡 메시지 전송 → 선택 동의
5. 앱 키 → REST API 키 복사 → config.py 의 KAKAO_REST_API_KEY 에 입력
"""

import webbrowser
import requests
import json
from pathlib import Path
from config import KAKAO_REST_API_KEY

REDIRECT_URI = "https://example.com"


def main():
    auth_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={KAKAO_REST_API_KEY}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=talk_message"
    )

    print("브라우저가 열립니다. 카카오 계정으로 로그인하세요.")
    webbrowser.open(auth_url)

    print("\n로그인 후 주소창의 URL 전체를 복사하세요.")
    print("예) https://example.com/?code=XXXXXX")
    url = input("\nURL 붙여넣기: ").strip()

    # URL에서 code 추출
    if "code=" in url:
        code = url.split("code=")[-1].split("&")[0]
    else:
        code = url  # 코드만 입력한 경우

    # 토큰 발급
    resp = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type":   "authorization_code",
            "client_id":    KAKAO_REST_API_KEY,
            "redirect_uri": REDIRECT_URI,
            "code":         code,
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    Path("kakao_token.json").write_text(
        json.dumps(data, ensure_ascii=False), encoding="utf-8"
    )
    print("\n✓ 카카오 토큰 저장 완료 (kakao_token.json)")
    print("이제 trader.py 를 실행하면 카카오톡 알림이 옵니다.")


if __name__ == "__main__":
    main()
