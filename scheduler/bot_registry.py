ACTIVE_BOTS = {}


def register_bot(
    user_id,
    process
):
    ACTIVE_BOTS[user_id] = process


def stop_bot(user_id):
    bot = ACTIVE_BOTS.get(
        user_id
    )

    if bot:
        bot.terminate()
        del ACTIVE_BOTS[user_id]


def bot_status(user_id):
    return user_id in ACTIVE_BOTS