from fastapi import APIRouter
from core.analytics import (
    NeuroLLaAnalytics
)

router = APIRouter()


@router.get("/analytics")
def get_analytics():
    analytics = NeuroLLaAnalytics()

    return {
        "total_trades": analytics.total_trades(),
        "win_rate": analytics.win_rate(),
        "total_pnl": analytics.total_pnl(),
        "profit_factor": analytics.profit_factor(),
        "sharpe_ratio": analytics.sharpe_ratio(),
        "max_drawdown": analytics.max_drawdown()
    }

@router.get("/analytics/equity")
def equity_curve():
    analytics = NeuroLLaAnalytics()

    trades = analytics.closed_trades()

    curve = []

    running = 0

    for t in trades:
        running += t.pnl
        curve.append(running)

    return {
        "equity_curve": curve
    }