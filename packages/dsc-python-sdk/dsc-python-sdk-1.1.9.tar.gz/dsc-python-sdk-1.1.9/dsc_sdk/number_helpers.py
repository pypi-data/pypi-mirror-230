from decimal import Decimal

__e18 = Decimal(10)**Decimal(18)
__e15 = Decimal(10)**Decimal(15)

def ether_to_wei(v: float) -> str:
    return str((__e18 * Decimal(v)).to_integral_value())

def finney_to_wei(v: float) -> str:
    return str((__e15 * Decimal(v)).to_integral_value())

def wei_to_ether(v: str) -> float:
    return float(Decimal(v) / __e18)