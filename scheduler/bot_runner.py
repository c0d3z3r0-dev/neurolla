import time
from commander import NeuroLLaCommander
from core.risk_guard import RiskGuard


def run_bot(
    broker,
    credentials
):
    commander = NeuroLLaCommander(
        broker=broker,
        credentials=credentials
    )

    guard = RiskGuard(user_id=1)

    while True:
         if not guard.can_trade():
             print(
                "RiskGuard blocked trading."
            )
        time.sleep(300)
        continue
