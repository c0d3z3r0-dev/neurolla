from fastapi import APIRouter, Depends
from core.analytics import NeuroLLaAnalytics
from server.auth import require_user

router = APIRouter()


@router.get("/analytics")
def get_analytics(user_id: int = Depends(require_user)):
    analytics = NeuroLLaAnalytics(user_id=user_id)

    try:
        return {
            "total_trades": analytics.total_trades(),
            "win_rate": analytics.win_rate(),
            "total_pnl": analytics.total_pnl(),
            "profit_factor": analytics.profit_factor(),
            "sharpe_ratio": analytics.sharpe_ratio(),
            "max_drawdown": analytics.max_drawdown()
        }
    finally:
        analytics.close()


@router.get("/analytics/equity")
def equity_curve(user_id: int = Depends(require_user)):
    analytics = NeuroLLaAnalytics(user_id=user_id)

    try:
        trades = analytics.closed_trades()

        curve = []
        running = 0

        for t in trades:
            running += t.pnl
            curve.append(running)

        return {
            "equity_curve": curve
        }
    finally:
        analytics.close()
