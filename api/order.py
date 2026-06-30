import requests
from config import BASE_URL, CANO, ACNT_PRDT_CD, MOCK
from api.auth import auth_headers

# 모의투자 / 실전투자 TR_ID
_BUY_TR  = "VTTC0802U" if MOCK else "TTTC0802U"
_SELL_TR = "VTTC0801U" if MOCK else "TTTC0801U"
_BAL_TR  = "VTTC8434R" if MOCK else "TTTC8434R"


def get_holdings() -> dict[str, int]:
    """보유 종목과 수량 반환 {symbol: quantity}"""
    resp = requests.get(
        f"{BASE_URL}/uapi/domestic-stock/v1/trading/inquire-balance",
        headers=auth_headers(_BAL_TR),
        params={
            "CANO":             CANO,
            "ACNT_PRDT_CD":     ACNT_PRDT_CD,
            "AFHR_FLPR_YN":     "N",
            "OFL_YN":           "",
            "INQR_DVSN":        "02",
            "UNPR_DVSN":        "01",
            "FUND_STTL_ICLD_YN":"N",
            "FNCG_AMT_AUTO_RDPT_YN":"N",
            "PRCS_DVSN":        "01",
            "CTX_AREA_FK100":   "",
            "CTX_AREA_NK100":   "",
        },
        timeout=10,
    )
    resp.raise_for_status()
    holdings = {}
    for item in resp.json().get("output1", []):
        symbol = item.get("pdno", "")
        qty    = int(item.get("hldg_qty", 0))
        if symbol and qty > 0:
            holdings[symbol] = qty
    return holdings


def buy_market(symbol: str, quantity: int) -> dict:
    """시장가 매수"""
    resp = requests.post(
        f"{BASE_URL}/uapi/domestic-stock/v1/trading/order-cash",
        headers=auth_headers(_BUY_TR),
        json={
            "CANO":         CANO,
            "ACNT_PRDT_CD": ACNT_PRDT_CD,
            "PDNO":         symbol,
            "ORD_DVSN":     "01",   # 시장가
            "ORD_QTY":      str(quantity),
            "ORD_UNPR":     "0",    # 시장가는 0
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def sell_market(symbol: str, quantity: int) -> dict:
    """시장가 매도"""
    resp = requests.post(
        f"{BASE_URL}/uapi/domestic-stock/v1/trading/order-cash",
        headers=auth_headers(_SELL_TR),
        json={
            "CANO":         CANO,
            "ACNT_PRDT_CD": ACNT_PRDT_CD,
            "PDNO":         symbol,
            "ORD_DVSN":     "01",   # 시장가
            "ORD_QTY":      str(quantity),
            "ORD_UNPR":     "0",
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()
