from asyncio import CancelledError, Queue, Task, create_task
from typing import Optional

from bot.sender.dataclasses import (
    AnswerCallbackQueryObj,
    BasicMessage,
    EditMessageTextObj,
    SendMessageObj,
    SendPhotoObj,
)
from bot.sender.tg_bot_api import TgBotApiSender


class Sender:
    def __init__(self, token: str, queue: Queue):
        self.tg_client: TgBotApiSender = TgBotApiSender(token=token)
        self.queue = queue
        self.is_running: bool = False
        self._task: Optional[Task] = None

    def start(self):
        self.is_running = True
        self._task = create_task(self._send())

    async def _send(self):
        while self.is_running:
            message = await self.queue.get()
            handler = self.select_message_handler(message=message)

            if handler:
                await handler(message=message)

            self.queue.task_done()

    def select_message_handler(self, message: Optional[BasicMessage]):
        message_to_handler = {
            SendMessageObj: self.tg_client.send_message,
            AnswerCallbackQueryObj: self.tg_client.answer_callback_query,
            EditMessageTextObj: self.tg_client.edit_message_text,
            SendPhotoObj: self.tg_client.send_photo,
        }
        return message_to_handler.get(message.__class__)

    async def stop(self):
        await self.queue.join()
        self.is_running = False
        self._task.cancel()
        try:
            await self._task
        except CancelledError:
            print("task_send is cancelled")
