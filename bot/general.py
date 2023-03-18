from asyncio import Queue, gather

from bot.poller.poller import Poller
from bot.sender.sender import Sender
from bot.worker.worker import Worker
from config.config import Config
from database.database import Database


class TgBot:
    def __init__(self, config: Config):
        self.id = config.tg_bot.id
        self.database = Database(config=config.tg_bot.database)
        self.update_queue = Queue()
        self.message_queue = Queue()
        self.poller = Poller(token=config.tg_bot.token, queue=self.update_queue)
        self.sender = Sender(token=config.tg_bot.token, queue=self.message_queue)
        self.worker = Worker(
            database=self.database,
            sender=self.sender,
            bot_id=self.id,
            update_queue=self.update_queue,
            message_queue=self.message_queue,
            workers_qty=config.tg_bot.workers_qty,
        )

    async def start_bot(self):
        await gather(
            self.database.connect(),
            self.poller.tg_client.set_main_menu(),
        )
        self.poller.start()
        self.worker.start()
        self.sender.start()

    async def stop_bot(self):
        await gather(
            self.poller.stop(),
            self.worker.stop(),
            self.sender.stop(),
            self.database.disconnect(),
        )
