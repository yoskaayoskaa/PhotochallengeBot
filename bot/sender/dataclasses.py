from dataclasses import dataclass
from typing import ClassVar, List, Optional, Type

from marshmallow import EXCLUDE, Schema
from marshmallow_dataclass import class_schema
from marshmallow_dataclass import dataclass as marshmallow_dataclass

from bot.poller.dataclasses import BasicMarshmallowDataclass, Message


@dataclass
class InlineKeyboardButton:
    text: str
    callback_data: str


@dataclass
class InlineKeyboardMarkup:
    inline_keyboard: List[List[InlineKeyboardButton]]


inline_keyboard_markup_schema = class_schema(InlineKeyboardMarkup)()


@dataclass
class BasicMessage:
    chat_id: int = 0


@dataclass
class SendMessageObj(BasicMessage):
    text: str = ""
    parse_mode: str = "HTML"
    keyboard: Optional[InlineKeyboardMarkup] = None


@dataclass
class AnswerCallbackQueryObj(BasicMessage):
    callback_query_id: str = ""
    text: str = ""
    show_alert: str = "False"


@dataclass
class EditMessageTextObj(BasicMessage):
    message_id: int = 0
    text: str = ""
    parse_mode: str = "HTML"
    keyboard: Optional[InlineKeyboardMarkup] = None


@dataclass
class SendPhotoObj(BasicMessage):
    photo: str = ""
    keyboard: Optional[InlineKeyboardMarkup] = None


@marshmallow_dataclass
class BasicResponse:
    ok: bool
    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


@marshmallow_dataclass
class PhotoSize(BasicMarshmallowDataclass):
    file_id: str


@marshmallow_dataclass
class UserProfilePhotos(BasicMarshmallowDataclass):
    total_count: int
    photos: List[List[PhotoSize]]


@marshmallow_dataclass
class GetUserProfilePhotosResponse(BasicResponse):
    result: UserProfilePhotos


@marshmallow_dataclass
class SendMessageResponse(BasicResponse):
    result: Message
