import json
from typing import List, Optional

from aiohttp import ClientSession

from bot.keyboard.menu import HELP_COMMAND, START_COMMAND
from bot.poller.dataclasses import (
    BasicUpdate,
    UpdateObjCallback,
    UpdateObjMessage,
    UpdateObjMyChatMember,
    bot_command_schema,
)


class TgBotApiPoller:
    def __init__(self, token: str = ""):
        self._token = token

    def get_request_url(self, method: str) -> str:
        return f"https://api.telegram.org/bot{self._token}/{method}"

    async def set_main_menu(self) -> dict:
        request_url = self.get_request_url(method="setMyCommands")
        commands = (START_COMMAND, HELP_COMMAND)
        commands_json = json.dumps([bot_command_schema.dump(command) for command in commands])
        params = {"commands": commands_json}

        async with ClientSession() as session:
            async with session.post(url=request_url, params=params) as response:
                return await response.json()

    async def get_updates(self, offset: int = None, timeout: int = 30) -> List[Optional[BasicUpdate]]:
        request_url = self.get_request_url(method="getUpdates")
        params = dict()

        if offset:
            params["offset"] = offset
        if timeout:
            params["timeout"] = timeout

        async with ClientSession() as session:
            async with session.get(url=request_url, params=params) as response:
                raw_response = await response.json()
                return [self.get_update_in_dataclass(raw_update) for raw_update in raw_response.get("result", [])]

    @staticmethod
    def get_update_in_dataclass(raw_update: dict) -> BasicUpdate:
        match tuple(raw_update.keys()):
            case _, "message":
                return UpdateObjMessage.Schema().load(raw_update)
            case _, "callback_query":
                return UpdateObjCallback.Schema().load(raw_update)
            case _, "my_chat_member":
                return UpdateObjMyChatMember.Schema().load(raw_update)
