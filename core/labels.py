import numpy as np
from core.config import TP_MULT, SL_MULT, LABEL_HORIZON


def triple_barrier_labels(
    close_prices,
    atr_values,
    tp_mult=TP_MULT,
    sl_mult=SL_MULT,
    horizon=LABEL_HORIZON
):
    """
    Single, shared triple-barrier labeling function.
    Label 2 = take-profit hit first (BUY signal in hindsight)
    Label 0 = stop-loss hit first  (SELL signal in hindsight)
    Label 1 = neither hit within horizon (HOLD)

    The lookahead window deliberately starts at i+1, not i, so the
    entry bar itself is never compared against its own barriers.
    The final `horizon` rows have no full lookahead window and are
    labeled HOLD (1) rather than silently dropped, so labels stay
    aligned 1:1 with the input arrays.
    """
    n = len(close_prices)
    labels = np.ones(n, dtype=np.int64)

    for i in range(n - horizon):
        entry = close_prices[i]
        atr = atr_values[i]

        if atr <= 0 or np.isnan(atr):
            continue

        upper = entry + (atr * tp_mult)
        lower = entry - (atr * sl_mult)

        future_window = close_prices[i + 1:i + 1 + horizon]

        hit_tp = np.any(future_window >= upper)
        hit_sl = np.any(future_window <= lower)

        if hit_tp and not hit_sl:
            labels[i] = 2
        elif hit_sl and not hit_tp:
            labels[i] = 0
        else:
            labels[i] = 1

    return labels
