def fractional_kelly(
    probability,
    reward_ratio=2.0,
    gamma=0.2
):
    p = probability
    b = reward_ratio

    kelly = (p * b - (1 - p)) / b

    return max(0, gamma * kelly)