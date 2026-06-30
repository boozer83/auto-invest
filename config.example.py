# 이 파일을 복사해서 config.py 로 이름 변경 후 값을 채워주세요
# cp config.example.py config.py

# 한국투자증권 OpenAPI 키 (https://apiportal.koreainvestment.com)
APP_KEY    = "YOUR_APP_KEY"
APP_SECRET = "YOUR_APP_SECRET"

# 계좌번호: 앞 8자리(CANO) + 뒤 2자리(ACNT_PRDT_CD)
# 예) 50123456-01 → CANO="50123456", ACNT_PRDT_CD="01"
CANO         = "YOUR_8_DIGIT_ACCOUNT"
ACNT_PRDT_CD = "01"

MOCK = True  # True = 모의투자 / False = 실전투자

BASE_URL = (
    "https://openapivts.koreainvestment.com:29443"  # 모의투자
    if MOCK else
    "https://openapi.koreainvestment.com:9443"       # 실전투자
)

# 타이탄 전략 대상 종목
STOCKS = {
    "SK하이닉스": "000660",
    "삼성SDI":   "006400",
    "삼성전자":  "005930",
    "삼성전기":  "009150",
}

# 타이탄 전략 파라미터
SHORT_MA = 20
LONG_MA  = 200

# 종목당 1회 매수금액 (원)
BUY_AMOUNT = 1_000_000  # 100만원

# 가격 체크 주기 (초)
CHECK_INTERVAL = 60
