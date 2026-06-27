from fastapi import APIRouter
from multiprocessing import Process

from scheduler.bot_runner import (
    run_bot
)

from scheduler.bot_registry import (
    register_bot,
    stop_bot,
    bot_status
)

router = APIRouter()


@router.post("/bot/start")
def start_bot(payload: dict):
    user_id = payload["user_id"]

    if bot_status(user_id):
        return {
            "status": "already running"
        }

    process = Process(
        target=run_bot,
        args=(
            payload["broker"],
            payload["credentials"]
        )
    )

    process.start()

    register_bot(
        user_id,
        process
    )

    return {
        "status": "bot started"
    }


@router.post("/bot/stop")
def stop_user_bot(payload: dict):
    user_id = payload["user_id"]

    stop_bot(user_id)

    return {
        "status": "bot stopped"
    }


@router.get("/bot/status/{user_id}")
def get_status(user_id: int):
    return {
        "running": bot_status(user_id)
    }