import json
from typing import List, Optional, Type

from aiohttp import ClientSession

from bot.sender.dataclasses import (
    AnswerCallbackQueryObj,
    EditMessageTextObj,
    GetUserProfilePhotosResponse,
    InlineKeyboardMarkup,
    PhotoSize,
    SendMessageObj,
    SendMessageResponse,
    SendPhotoObj,
    inline_keyboard_markup_schema,
)


class TgBotApiSender:
    def __init__(self, token: str = ""):
        self._token = token

    def get_request_url(self, method: str) -> str:
        return f"https://api.telegram.org/bot{self._token}/{method}"

    async def get_user_profile_photos(self, user_id: int, offset: int = 0) -> List[List[PhotoSize]]:
        request_url = self.get_request_url(method="getUserProfilePhotos")
        params = {"user_id": user_id, "offset": offset}

        async with ClientSession() as session:
            async with session.get(url=request_url, params=params) as response:
                raw_response = await response.json()
                obj_response = GetUserProfilePhotosResponse.Schema().load(raw_response)
                return obj_response.result.photos

    async def send_message(self, message: SendMessageObj) -> SendMessageResponse:
        request_url = self.get_request_url(method="sendMessage")
        params = {
            "chat_id": message.chat_id,
            "text": message.text,
            "parse_mode": message.parse_mode,
        }

        return await self.handle_post_request(
            marshmallow_dataclass=SendMessageResponse,
            request_url=request_url,
            params=params,
            keyboard=message.keyboard,
        )

    async def answer_callback_query(self, message: AnswerCallbackQueryObj) -> dict:
        request_url = self.get_request_url(method="answerCallbackQuery")
        params = {
            "callback_query_id": message.callback_query_id,
            "text": message.text,
            "show_alert": message.show_alert,
        }

        async with ClientSession() as session:
            async with session.post(url=request_url, params=params) as response:
                raw_response = await response.json()
                return raw_response

    async def edit_message_text(self, message: EditMessageTextObj) -> SendMessageResponse:
        request_url = self.get_request_url(method="editMessageText")
        params = {
            "chat_id": message.chat_id,
            "message_id": message.message_id,
            "text": message.text,
            "parse_mode": message.parse_mode,
        }

        return await self.handle_post_request(
            marshmallow_dataclass=SendMessageResponse,
            request_url=request_url,
            params=params,
            keyboard=message.keyboard,
        )

    async def send_photo(self, message: SendPhotoObj) -> SendMessageResponse:
        request_url = self.get_request_url(method="sendPhoto")
        params = {"chat_id": message.chat_id, "photo": message.photo}

        return await self.handle_post_request(
            marshmallow_dataclass=SendMessageResponse,
            request_url=request_url,
            params=params,
            keyboard=message.keyboard,
        )

    async def handle_post_request(
        self,
        marshmallow_dataclass: Type[SendMessageResponse],
        request_url: str,
        params: dict,
        keyboard: Optional[InlineKeyboardMarkup] = None,
    ) -> SendMessageResponse:
        if keyboard:
            params["reply_markup"] = self.convert_inline_keyboard_to_json(keyboard=keyboard)

        async with ClientSession() as session:
            async with session.post(url=request_url, params=params) as response:
                raw_response = await response.json()
                return marshmallow_dataclass.Schema().load(raw_response)

    @staticmethod
    def convert_inline_keyboard_to_json(keyboard: InlineKeyboardMarkup) -> json:
        keyboard_dict = inline_keyboard_markup_schema.dump(keyboard)
        keyboard_json = json.dumps(keyboard_dict)
        return keyboard_json
