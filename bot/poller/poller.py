from asyncio import CancelledError, Queue, Task, create_task
from typing import List, Optional

from bot.poller.dataclasses import BasicUpdate
from bot.poller.tg_bot_api import TgBotApiPoller


class Poller:
    def __init__(self, token: str, queue: Queue):
        self.tg_client: TgBotApiPoller = TgBotApiPoller(token=token)
        self.queue = queue
        self.is_running: bool = False
        self._task: Optional[Task] = None

    async def _poll(self):
        offset = 0
        while self.is_running:
            updates: List[Optional[BasicUpdate]] = await self.tg_client.get_updates(offset=offset, timeout=30)

            for update in updates:
                offset = update.update_id + 1
                await self.queue.put(update)

    def start(self):
        self.is_running = True
        self._task = create_task(self._poll())

    async def stop(self):
        self.is_running = False
        self._task.cancel()
        try:
            await self._task
        except CancelledError:
            print("task_poll is cancelled")
