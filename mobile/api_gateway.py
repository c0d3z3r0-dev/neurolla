from fastapi import FastAPI
from commander import NeuroLLaCommander

app = FastAPI()

commander = NeuroLLaCommander()


@app.get("/signal/{symbol}")
def get_signal(symbol: str):
    ranked = commander.scanner.scan()

    for signal in ranked:
        if signal["symbol"] == symbol:
            return signal

    return {
        "status": "No signal"
    }