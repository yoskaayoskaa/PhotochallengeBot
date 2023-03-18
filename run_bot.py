from asyncio import get_event_loop

from bot.general import TgBot
from config.config import Config, setup_config


def run_bot():
    config: Config = setup_config()

    loop = get_event_loop()

    tg_bot = TgBot(config=config)

    try:
        loop.create_task(tg_bot.start_bot())
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(tg_bot.stop_bot())


if __name__ == "__main__":
    run_bot()
