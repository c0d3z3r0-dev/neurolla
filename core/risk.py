from core.config import MAX_RISK_PER_TRADE


def fractional_kelly(
    probability,
    reward_ratio=2.0,
    gamma=0.2
):
    """
    Returns the fraction of equity to risk on a trade, using a
    fractional Kelly criterion damped by `gamma` and hard-capped at
    MAX_RISK_PER_TRADE.

    The cap matters: Kelly sizing alone has no ceiling, and a string of
    high-confidence trades could otherwise risk an ever-larger fraction
    of the account, compounding equity (and drawdown risk) far faster
    than the risk policy in core.config intends.
    """
    p = probability
    b = reward_ratio

    kelly = (p * b - (1 - p)) / b

    fraction = max(0, gamma * kelly)

    return min(fraction, MAX_RISK_PER_TRADE)
