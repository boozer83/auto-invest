import pandas as pd
from config import SHORT_MA, LONG_MA


class TitanStrategy:
    """
    타이탄 투자 전략
    - 매수: 현재가가 20MA 위로 돌파 AND 현재가가 200MA 위
    - 매도: 현재가가 20MA 아래로 이탈
    """

    def __init__(self):
        # 직전 체크 때 20MA 위에 있었는지 기록 {symbol: bool}
        self._prev_above_ma20: dict[str, bool] = {}

    def calculate_mas(self, df: pd.DataFrame) -> tuple[float, float]:
        """df: 'close' 컬럼을 가진 일봉 DataFrame (오래된 것 → 최신 순)"""
        if len(df) < LONG_MA:
            raise ValueError(f"데이터 부족: {len(df)}개 (최소 {LONG_MA}개 필요)")

        closes = df["close"].tolist()
        ma20  = sum(closes[-SHORT_MA:]) / SHORT_MA
        ma200 = sum(closes[-LONG_MA:])  / LONG_MA
        return ma20, ma200

    def get_signal(
        self,
        symbol: str,
        ma20: float,
        ma200: float,
        current_price: float,
    ) -> str:
        """'BUY' / 'SELL' / 'HOLD' 반환"""
        above_ma20  = current_price > ma20
        above_ma200 = current_price > ma200

        prev = self._prev_above_ma20.get(symbol)
        self._prev_above_ma20[symbol] = above_ma20

        if prev is None:
            # 첫 번째 체크: 기준점 설정만 하고 신호 없음
            return "HOLD"

        if not prev and above_ma20 and above_ma200:
            return "BUY"   # 20MA 상향 돌파 + 200MA 위

        if prev and not above_ma20:
            return "SELL"  # 20MA 하향 이탈

        return "HOLD"
