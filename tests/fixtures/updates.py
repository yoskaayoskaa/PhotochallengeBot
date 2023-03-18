import pytest

from bot.poller.dataclasses import UpdateObjCallback, UpdateObjMessage, UpdateObjMyChatMember


@pytest.fixture
def update_message_start() -> UpdateObjMessage:
    raw_update = {
        "update_id": 12345,
        "message": {
            "message_id": 1234,
            "from": {
                "id": 1,
                "first_name": "first_name",
                "last_name": "last_name",
                "username": "username",
            },
            "chat": {
                "id": -123,
                "title": "Photo_Bot_Test",
                "type": "group",
            },
            "text": "/start@kts_photochallenge_bot",
        },
    }
    return UpdateObjMessage.Schema().load(raw_update)


@pytest.fixture
def update_callback(tg_bot) -> UpdateObjCallback:
    raw_update = {
        "update_id": 12345,
        "callback_query": {
            "id": "1",
            "from": {
                "id": 242360,
                "first_name": "first_name",
                "last_name": "last_name",
                "username": "username",
            },
            "message": {
                "message_id": 1234,
                "from": {
                    "id": tg_bot.worker.bot_id,
                    "first_name": "PhotochallengeBot",
                    "username": "kts_photochallenge_bot",
                },
                "chat": {
                    "id": -123,
                    "title": "Photo_Bot_Test",
                    "type": "group",
                },
                "text": "text",
            },
            "data": "callback",
        },
    }
    return UpdateObjCallback.Schema().load(raw_update)


@pytest.fixture
def update_status_member(tg_bot) -> UpdateObjMyChatMember:
    raw_update = {
        "update_id": 12345,
        "my_chat_member": {
            "chat": {
                "id": -123,
                "title": "Photo_Bot_Test",
                "type": "group",
            },
            "from": {
                "id": 1,
                "first_name": "first_name",
                "last_name": "last_name",
                "username": "username",
            },
            "new_chat_member": {
                "user": {
                    "id": tg_bot.worker.bot_id,
                    "first_name": "PhotochallengeBot",
                    "username": "kts_photochallenge_bot",
                },
                "status": "member",
            },
        },
    }
    return UpdateObjMyChatMember.Schema().load(raw_update)
