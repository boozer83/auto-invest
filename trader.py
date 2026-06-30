import time
from datetime import datetime
from config import STOCKS, BUY_AMOUNT, CHECK_INTERVAL
from api.market import fetch_current_price, fetch_history
from api.order  import get_holdings, buy_market, sell_market
from strategy.titan import TitanStrategy
from logger import log_signal, log_order, log_error, log_info


MARKET_OPEN  = (9,  0)
MARKET_CLOSE = (15, 30)


def is_market_open() -> bool:
    now = datetime.now()
    if now.weekday() >= 5:  # 토/일
        return False
    t = (now.hour, now.minute)
    return MARKET_OPEN <= t < MARKET_CLOSE


def calc_buy_qty(price: float) -> int:
    return max(1, int(BUY_AMOUNT // price))


def main():
    log_info("=== 타이탄 자동매매 시작 ===")
    strategy = TitanStrategy()

    # ── 1. 과거 데이터 로딩 (MA 계산용) ──────────────────────────
    log_info("과거 데이터 로딩 중...")
    history: dict[str, object] = {}
    mas:     dict[str, tuple]  = {}  # {symbol: (ma20, ma200)}

    for name, symbol in STOCKS.items():
        try:
            df = fetch_history(symbol)
            ma20, ma200 = strategy.calculate_mas(df)
            history[symbol] = df
            mas[symbol]     = (ma20, ma200)
            log_info(f"  {name}: MA20={ma20:,.0f}  MA200={ma200:,.0f}")
        except Exception as e:
            log_error(f"  {name} 데이터 로딩 실패: {e}")

    # ── 2. 현재 보유 종목 확인 ─────────────────────────────────────
    try:
        positions = get_holdings()  # {symbol: qty}
        log_info(f"현재 보유: {positions if positions else '없음'}")
    except Exception as e:
        log_error(f"보유 조회 실패: {e}")
        positions = {}

    log_info(f"체크 주기: {CHECK_INTERVAL}초 / 매수금액: {BUY_AMOUNT:,}원")
    log_info("─" * 50)

    # ── 3. 메인 루프 ───────────────────────────────────────────────
    while True:
        try:
            if not is_market_open():
                log_info("장 마감 또는 휴장일. 대기 중...")
                time.sleep(60)
                continue

            for name, symbol in STOCKS.items():
                if symbol not in mas:
                    continue
                try:
                    price       = fetch_current_price(symbol)
                    ma20, ma200 = mas[symbol]
                    signal      = strategy.get_signal(symbol, ma20, ma200, price)

                    log_signal(name, symbol, signal, price, ma20, ma200)

                    if signal == "BUY" and symbol not in positions:
                        qty  = calc_buy_qty(price)
                        resp = buy_market(symbol, qty)
                        if resp.get("rt_cd") == "0":
                            positions[symbol] = qty
                            log_order("매수", name, symbol, price, qty)
                        else:
                            log_error(f"매수 실패: {resp}")

                    elif signal == "SELL" and symbol in positions:
                        qty  = positions[symbol]
                        resp = sell_market(symbol, qty)
                        if resp.get("rt_cd") == "0":
                            del positions[symbol]
                            log_order("매도", name, symbol, price, qty)
                        else:
                            log_error(f"매도 실패: {resp}")

                except Exception as e:
                    log_error(f"{name} 처리 오류: {e}")

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            log_info("사용자 종료")
            break
        except Exception as e:
            log_error(f"루프 오류: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
