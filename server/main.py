from fastapi import FastAPI
from server.database import Base, engine
from server.routes.users import router as users_router
from server.routes.brokers import router as brokers_router
from server.routes.configs import router as configs_router
from server.routes.bots import router as bots_router

import server.models
from server.routes.auth import router as auth_router
from server.routes.trades import (
    router as trades_router
)
from server.routes.analytics import (
    router as analytics_router
)
from server.routes.risk import (
    router as risk_router
)


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(users_router)
app.include_router(brokers_router)
app.include_router(configs_router)
app.include_router(bots_router)
app.include_router(auth_router)
app.include_router(trades_router)
app.include_router(
    analytics_router
)
app.include_router(risk_router)

@app.get("/")
def root():
    return {
        "status": "NeuroLLa API online"
    }