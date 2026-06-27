import numpy as np


def triple_barrier_labels(
    close_prices,
    atr_values,
    tp_mult=2.0,
    sl_mult=1.0,
    horizon=48
):
    labels = []

    for i in range(len(close_prices) - horizon):
        start_price = close_prices[i]

        upper = start_price + (atr_values[i] * tp_mult)
        lower = start_price - (atr_values[i] * sl_mult)

        future_window = close_prices[i:i+horizon]

        label = 1

        for price in future_window:
            if price >= upper:
                label = 2
                break

            elif price <= lower:
                label = 0
                break

        labels.append(label)

    return np.array(labels)