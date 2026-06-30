import logging
from datetime import datetime
from pathlib import Path

Path("logs").mkdir(exist_ok=True)

_logger = logging.getLogger("titan")
_logger.setLevel(logging.DEBUG)

_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")

# 콘솔 출력
_ch = logging.StreamHandler()
_ch.setFormatter(_fmt)
_logger.addHandler(_ch)

# 파일 출력 (날짜별)
_fh = logging.FileHandler(f"logs/{datetime.today().strftime('%Y%m%d')}.log", encoding="utf-8")
_fh.setFormatter(_fmt)
_logger.addHandler(_fh)


def log_signal(name: str, symbol: str, signal: str, price: float, ma20: float, ma200: float):
    _logger.info(f"[{signal:4s}] {name}({symbol}) 현재가={price:,.0f} MA20={ma20:,.0f} MA200={ma200:,.0f}")


def log_order(action: str, name: str, symbol: str, price: float, qty: int):
    amount = price * qty
    _logger.info(f"[주문] {action} {name}({symbol}) {qty}주 @ {price:,.0f}원 = {amount:,.0f}원")


def log_error(msg: str):
    _logger.error(msg)


def log_info(msg: str):
    _logger.info(msg)
