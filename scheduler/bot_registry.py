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
    bot = ACTIVE_BOTS.get(user_id)

    if bot is None:
        return False

    # A process can crash without anyone calling stop_bot, in which case
    # it would still show up as "running" by dict membership alone.
    # is_alive() reflects the real OS process state.
    if not bot.is_alive():
        del ACTIVE_BOTS[user_id]
        return False

    return True
