from typing import TYPE_CHECKING, Optional

from bot.keyboard.keyboards import (
    EXIT_CALLBACK,
    FINISH_REGISTRATION_CALLBACK,
    FINISH_ROUND_CALLBACK,
    FIRST_PHOTO_CALLBACK,
    NEXT_ROUND_CALLBACK,
    PLAY_ROUND_CALLBACK,
    SECOND_PHOTO_CALLBACK,
    START_REGISTRATION_CALLBACK,
    STATISTICS_CALLBACK,
    USER_REGISTER_CALLBACK,
)
from bot.keyboard.menu import HELP_COMMAND, START_COMMAND
from bot.models import Game
from bot.poller.dataclasses import BasicUpdate, UpdateObjCallback, UpdateObjMessage, UpdateObjMyChatMember
from bot.worker.fsm import BEGINNING_STATE, FINISH_ROUND_STATE, GAMEPLAY_STATE, REGISTRATION_STATE, START_ROUND_STATE
from bot.worker.status import STATUS_LEFT, STATUS_MEMBER

if TYPE_CHECKING:
    from bot.worker.worker import Worker


class FilterUpdate:
    def __init__(self, worker: "Worker"):
        self.worker = worker

        self.status_to_handlers = {
            STATUS_MEMBER: self.worker.handle_status_member_update,
            STATUS_LEFT: self.worker.handle_status_left_update,
        }

        self.commands_to_handlers = {
            HELP_COMMAND.command: self.worker.handle_help_update,
        }

        self.states_to_handlers = {
            BEGINNING_STATE: self.worker.handle_beginning_state,
            REGISTRATION_STATE: self.worker.handle_registration_state,
            GAMEPLAY_STATE: self.worker.handle_gameplay_state,
            START_ROUND_STATE: self.worker.handle_start_round_state,
            FINISH_ROUND_STATE: self.worker.handle_finish_round_state,
        }

        self.callbacks_to_handlers = {
            START_REGISTRATION_CALLBACK: self.worker.handle_start_registration_callback,
            STATISTICS_CALLBACK: self.worker.handle_statistics_callback,
            USER_REGISTER_CALLBACK: self.worker.handle_user_register_callback,
            FINISH_REGISTRATION_CALLBACK: self.worker.handle_finish_registration_callback,
            PLAY_ROUND_CALLBACK: self.worker.handle_play_round_callback,
            FIRST_PHOTO_CALLBACK: self.worker.handle_first_photo_callback,
            SECOND_PHOTO_CALLBACK: self.worker.handle_second_photo_callback,
            FINISH_ROUND_CALLBACK: self.worker.handle_finish_round_callback,
            NEXT_ROUND_CALLBACK: self.worker.handle_next_round_callback,
            EXIT_CALLBACK: self.worker.handle_exit_callback,
        }

    @staticmethod
    def get_current_chat_id(update: Optional[BasicUpdate]) -> int:
        if isinstance(update, UpdateObjMyChatMember):
            return update.my_chat_member.chat.id

        if isinstance(update, UpdateObjCallback):
            return update.callback_query.message.chat.id

        if isinstance(update, UpdateObjMessage):
            return update.message.chat.id

    def filter_incoming_update(self, update: Optional[BasicUpdate], game: Optional[Game]) -> classmethod:
        if isinstance(update, UpdateObjMyChatMember):
            return self.status_to_handlers.get(update.my_chat_member.new_chat_member.status)

        if isinstance(update, UpdateObjCallback):
            return self.callbacks_to_handlers.get(update.callback_query.data)

        if isinstance(update, UpdateObjMessage):
            if update.message.text is not None:
                if START_COMMAND.command in update.message.text:
                    return self.states_to_handlers.get(game.bot_state)

                if HELP_COMMAND.command in update.message.text:
                    return self.commands_to_handlers.get(HELP_COMMAND.command)
