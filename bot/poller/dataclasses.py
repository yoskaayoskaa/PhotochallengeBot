from dataclasses import dataclass, field
from typing import ClassVar, Optional, Type

from marshmallow import EXCLUDE, Schema
from marshmallow_dataclass import class_schema
from marshmallow_dataclass import dataclass as marshmallow_dataclass


@marshmallow_dataclass
class BasicMarshmallowDataclass:
    class Meta:
        unknown = EXCLUDE


@marshmallow_dataclass
class BasicUpdate:
    update_id: int
    Schema: ClassVar[Type[Schema]] = Schema

    class Meta:
        unknown = EXCLUDE


@marshmallow_dataclass
class MessageFrom(BasicMarshmallowDataclass):  # User
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None


@marshmallow_dataclass
class Chat(BasicMarshmallowDataclass):
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@marshmallow_dataclass
class Message(BasicMarshmallowDataclass):
    message_id: int
    from_: MessageFrom = field(metadata={"data_key": "from"})  # User
    chat: Chat
    text: Optional[str] = None


@marshmallow_dataclass
class UpdateObjMessage(BasicUpdate):
    message: Message


@marshmallow_dataclass
class CallbackQuery(BasicMarshmallowDataclass):
    id: str
    from_: MessageFrom = field(metadata={"data_key": "from"})  # User
    message: Message
    data: str


@marshmallow_dataclass
class UpdateObjCallback(BasicUpdate):
    callback_query: CallbackQuery


@marshmallow_dataclass
class NewChatMember(BasicMarshmallowDataclass):
    user: MessageFrom  # User
    status: str


@marshmallow_dataclass
class MyChatMember(BasicMarshmallowDataclass):
    chat: Chat
    from_: MessageFrom = field(metadata={"data_key": "from"})  # User
    new_chat_member: NewChatMember


@marshmallow_dataclass
class UpdateObjMyChatMember(BasicUpdate):
    my_chat_member: MyChatMember


@dataclass
class BotCommand:
    command: str
    description: str


bot_command_schema = class_schema(BotCommand)()
