import requests
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta
from config import BASE_URL
from api.auth import auth_headers


def fetch_current_price(symbol: str) -> float:
    """KIS API로 현재가 실시간 조회"""
    resp = requests.get(
        f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price",
        headers=auth_headers("FHKST01010100"),
        params={
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD":         symbol,
        },
        timeout=10,
    )
    resp.raise_for_status()
    output = resp.json().get("output", {})
    return float(output["stck_prpr"])  # 현재가


def fetch_history(symbol: str, days: int = 250) -> pd.DataFrame:
    """FinanceDataReader로 일봉 종가 조회 (MA 계산용)"""
    end   = datetime.today()
    start = end - timedelta(days=days * 2)  # 주말/공휴일 감안해 넉넉하게

    df = fdr.DataReader(symbol, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    df = df[["Close"]].rename(columns={"Close": "close"})
    df = df.dropna().tail(days).reset_index(drop=True)
    return df
