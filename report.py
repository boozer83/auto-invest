import json
from datetime import datetime
from pathlib import Path
from api.market import fetch_current_price
from notifier import kakao
from logger import log_error

TRADES_FILE    = Path("trades.json")
POSITIONS_FILE = Path("positions.json")


# ── 거래 기록 ────────────────────────────────────────────────

def load_trades() -> list:
    if TRADES_FILE.exists():
        return json.loads(TRADES_FILE.read_text(encoding="utf-8"))
    return []


def save_trade(action: str, name: str, symbol: str, price: float, qty: int):
    trades = load_trades()
    trades.append({
        "date":   datetime.now().strftime("%Y-%m-%d"),
        "time":   datetime.now().strftime("%H:%M:%S"),
        "action": action,
        "name":   name,
        "symbol": symbol,
        "price":  price,
        "qty":    qty,
        "amount": price * qty,
    })
    TRADES_FILE.write_text(json.dumps(trades, ensure_ascii=False, indent=2), encoding="utf-8")


# ── 포지션 기록 (매입가 추적) ────────────────────────────────

def load_positions() -> dict:
    if POSITIONS_FILE.exists():
        return json.loads(POSITIONS_FILE.read_text(encoding="utf-8"))
    return {}


def save_positions(positions: dict):
    POSITIONS_FILE.write_text(json.dumps(positions, ensure_ascii=False, indent=2), encoding="utf-8")


def add_position(name: str, symbol: str, price: float, qty: int):
    positions = load_positions()
    positions[symbol] = {
        "name":       name,
        "qty":        qty,
        "buy_price":  price,
        "buy_date":   datetime.now().strftime("%Y-%m-%d"),
    }
    save_positions(positions)


def remove_position(symbol: str):
    positions = load_positions()
    positions.pop(symbol, None)
    save_positions(positions)


# ── 일일 리포트 ──────────────────────────────────────────────

def generate_daily_report():
    today     = datetime.now().strftime("%Y-%m-%d")
    trades    = load_trades()
    positions = load_positions()

    today_trades = [t for t in trades if t["date"] == today]

    lines = [f"[타이탄 일일 리포트] {today}\n"]

    # 오늘 거래 내역
    if today_trades:
        lines.append("── 오늘 거래 ──")
        realized_pnl = 0
        sell_trades = [t for t in today_trades if t["action"] == "SELL"]

        for t in today_trades:
            mark = "매수" if t["action"] == "BUY" else "매도"
            lines.append(f"{mark} {t['name']} {t['qty']}주 @ {t['price']:,.0f}원")

        # 실현손익: 오늘 매도한 종목의 손익 (매입가 기준)
        for t in sell_trades:
            symbol = t["symbol"]
            # trades에서 가장 최근 매수가 찾기
            buy_trades = [b for b in trades if b["symbol"] == symbol and b["action"] == "BUY" and b["date"] <= today]
            if buy_trades:
                buy_price  = buy_trades[-1]["price"]
                pnl        = (t["price"] - buy_price) * t["qty"]
                pnl_pct    = (t["price"] - buy_price) / buy_price * 100
                realized_pnl += pnl
                lines.append(f"  └ 실현손익: {pnl:+,.0f}원 ({pnl_pct:+.1f}%)")

        if sell_trades:
            lines.append(f"\n오늘 실현손익 합계: {realized_pnl:+,.0f}원")
    else:
        lines.append("── 오늘 거래 없음 ──")

    # 현재 보유 종목 평가
    if positions:
        lines.append("\n── 현재 보유 ──")
        total_eval   = 0
        total_invest = 0

        for symbol, pos in positions.items():
            try:
                cur_price  = fetch_current_price(symbol)
                invest     = pos["buy_price"] * pos["qty"]
                eval_amt   = cur_price * pos["qty"]
                pnl        = eval_amt - invest
                pnl_pct    = pnl / invest * 100
                total_eval   += eval_amt
                total_invest += invest
                lines.append(
                    f"{pos['name']} {pos['qty']}주\n"
                    f"  매입 {pos['buy_price']:,.0f} → 현재 {cur_price:,.0f} "
                    f"({pnl_pct:+.1f}%) {pnl:+,.0f}원"
                )
            except Exception as e:
                log_error(f"평가금액 조회 실패 {symbol}: {e}")

        if total_invest > 0:
            total_pnl     = total_eval - total_invest
            total_pnl_pct = total_pnl / total_invest * 100
            lines.append(f"\n평가손익 합계: {total_pnl:+,.0f}원 ({total_pnl_pct:+.1f}%)")
    else:
        lines.append("\n── 보유 종목 없음 ──")

    msg = "\n".join(lines)
    try:
        kakao.send(msg)
    except Exception as e:
        log_error(f"일일 리포트 전송 실패: {e}")
