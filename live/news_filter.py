from datetime import datetime


class NewsFilter:
    def __init__(self):
        self.blackout_hours = [
            12, 13, 14
        ]

    def is_safe(self):
        now = datetime.utcnow()

        if now.hour in self.blackout_hours:
            return False

        return True