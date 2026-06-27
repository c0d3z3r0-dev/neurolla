from fastapi import APIRouter, Depends
from multiprocessing import Process

from scheduler.bot_runner import run_bot
from scheduler.bot_registry import register_bot, stop_bot, bot_status
from server.auth import require_user

router = APIRouter()


@router.post("/bot/start")
def start_bot(payload: dict, user_id: int = Depends(require_user)):
    if bot_status(user_id):
        return {
            "status": "already running"
        }

    process = Process(
        target=run_bot,
        args=(
            payload["broker"],
            payload["credentials"],
            user_id
        )
    )

    process.start()

    register_bot(user_id, process)

    return {
        "status": "bot started"
    }


@router.post("/bot/stop")
def stop_user_bot(user_id: int = Depends(require_user)):
    stop_bot(user_id)

    return {
        "status": "bot stopped"
    }


@router.get("/bot/status")
def get_status(user_id: int = Depends(require_user)):
    return {
        "running": bot_status(user_id)
    }
