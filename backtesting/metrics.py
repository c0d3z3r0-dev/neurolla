import numpy as np


def win_rate(trades):
    if len(trades) == 0:
        return 0

    wins = [x for x in trades if x > 0]

    return len(wins) / len(trades)


def profit_factor(trades):
    gross_profit = sum(
        x for x in trades if x > 0
    )

    gross_loss = abs(
        sum(x for x in trades if x < 0)
    )

    if gross_loss == 0:
        return float("inf")

    return gross_profit / gross_loss


def expectancy(trades):
    if len(trades) == 0:
        return 0

    return np.mean(trades)


def sharpe_ratio(
    returns,
    risk_free=0
):
    if len(returns) == 0:
        return 0

    excess = np.array(returns) - risk_free

    if np.std(excess) == 0:
        return 0

    return (
        np.mean(excess) /
        np.std(excess)
    ) * np.sqrt(252)


def max_drawdown(equity_curve):
    peak = equity_curve[0]
    max_dd = 0

    for equity in equity_curve:
        if equity > peak:
            peak = equity

        dd = (
            peak - equity
        ) / peak

        if dd > max_dd:
            max_dd = dd

    return max_dd


def max_consecutive_losses(trades):
    max_streak = 0
    current_streak = 0

    for trade in trades:
        if trade < 0:
            current_streak += 1

            if current_streak > max_streak:
                max_streak = current_streak
        else:
            current_streak = 0

    return max_streak