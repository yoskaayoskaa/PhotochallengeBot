from asyncio import CancelledError, Queue, Task, create_task, gather, sleep
from random import sample
from typing import List, Optional

from bot.keyboard.keyboards import (
    BEGINNING_KEYBOARD,
    FINISH_GAME_KEYBOARD,
    FINISH_ROUND_KEYBOARD,
    FIRST_PHOTO_KEYBOARD,
    GAMEPLAY_KEYBOARD,
    NEXT_ROUND_KEYBOARD,
    REGISTRATION_KEYBOARD,
    SECOND_PHOTO_KEYBOARD,
)
from bot.keyboard.lexicon_ru import LEXICON_RU
from bot.models import Game, User
from bot.poller.dataclasses import UpdateObjCallback, UpdateObjMessage, UpdateObjMyChatMember
from bot.sender.dataclasses import AnswerCallbackQueryObj, EditMessageTextObj, SendMessageObj, SendPhotoObj
from bot.sender.sender import Sender
from bot.worker.accessor import BotAccessor
from bot.worker.filter import FilterUpdate
from bot.worker.fsm import (
    BEGINNING_STATE,
    DELETED_STATE,
    FINISH_ROUND_STATE,
    GAMEPLAY_STATE,
    REGISTRATION_STATE,
    START_ROUND_STATE,
)
from bot.worker.status import FIRST_PHOTO, SECOND_PHOTO
from database.database import Database


class Worker:
    def __init__(
        self,
        database: Database,
        sender: Sender,
        bot_id: int,
        update_queue: Queue,
        message_queue: Queue,
        workers_qty: int,
    ):
        self.accessor: BotAccessor = BotAccessor(database=database)
        self.sender = sender
        self.bot_id = bot_id
        self.filter: FilterUpdate = FilterUpdate(worker=self)
        self.update_queue = update_queue
        self.message_queue = message_queue
        self.workers_qty = workers_qty
        self.is_running: bool = False
        self._tasks: List[Task] = list()

    def start(self):
        self.is_running = True
        self._tasks = [create_task(self._work()) for _ in range(self.workers_qty)]

    async def _work(self):
        while self.is_running:
            update = await self.update_queue.get()
            chat_id = self.filter.get_current_chat_id(update=update)
            game = await self.accessor.get_game_dataclass(chat_id=chat_id)  # Game or None
            handler = self.filter.filter_incoming_update(update=update, game=game)

            if handler:
                await handler(update=update, game=game)

            self.update_queue.task_done()

    async def handle_status_member_update(self, update: UpdateObjMyChatMember, game: Optional[Game]) -> None:
        if update.my_chat_member.new_chat_member.user.id == self.bot_id:
            chat_id = update.my_chat_member.chat.id
            message = SendMessageObj(chat_id=chat_id, text=LEXICON_RU["member"])
            if not game:
                await gather(self.accessor.create_game_model(chat_id=chat_id), self.message_queue.put(message))
            else:
                await gather(
                    self.accessor.change_current_bot_state(chat_id=chat_id, new_bot_state=BEGINNING_STATE),
                    self.message_queue.put(message),
                )

    async def handle_status_left_update(self, update: UpdateObjMyChatMember, game: Optional[Game]):
        if update.my_chat_member.new_chat_member.user.id == self.bot_id:
            await self.accessor.change_current_bot_state(chat_id=game.chat_id, new_bot_state=DELETED_STATE)
            if game.accounts:
                await self.accessor.delete_all_current_players(chat_id=game.chat_id)

    async def handle_beginning_state(self, update: UpdateObjMessage, game: Optional[Game]):
        await self.message_queue.put(
            SendMessageObj(
                chat_id=game.chat_id,
                text=LEXICON_RU["beginning"],
                keyboard=BEGINNING_KEYBOARD,
            )
        )

    async def handle_registration_state(self, update: UpdateObjMessage, game: Optional[Game]):
        await self.message_queue.put(
            SendMessageObj(
                chat_id=game.chat_id,
                text=LEXICON_RU["registration"].format(players_num=len(game.accounts)),
                keyboard=REGISTRATION_KEYBOARD,
            )
        )

    async def handle_gameplay_state(self, update: UpdateObjMessage, game: Optional[Game]):
        await self.message_queue.put(
            SendMessageObj(
                chat_id=game.chat_id,
                text=LEXICON_RU["gameplay"],
                keyboard=GAMEPLAY_KEYBOARD,
            )
        )

    async def handle_start_round_state(self, update: UpdateObjMessage, game: Optional[Game]):
        await self.message_queue.put(SendMessageObj(chat_id=game.chat_id, text=LEXICON_RU["start_round"]))

    async def handle_finish_round_state(self, update: UpdateObjMessage, game: Optional[Game]):
        await self.message_queue.put(
            SendMessageObj(
                chat_id=game.chat_id,
                text=LEXICON_RU["next_round"],
                keyboard=NEXT_ROUND_KEYBOARD,
            )
        )

    async def handle_help_update(self, update: UpdateObjMessage, game: Optional[Game]):
        await self.message_queue.put(SendMessageObj(chat_id=game.chat_id, text=LEXICON_RU["help"]))

    async def handle_start_registration_callback(self, update: UpdateObjCallback, game: Optional[Game]):
        await gather(
            self.accessor.change_current_bot_state(chat_id=game.chat_id, new_bot_state=REGISTRATION_STATE),
            self.message_queue.put(
                SendMessageObj(
                    chat_id=game.chat_id,
                    text=LEXICON_RU["registration"].format(players_num=len(game.accounts)),
                    keyboard=REGISTRATION_KEYBOARD,
                )
            ),
        )

    async def handle_statistics_callback(self, update: UpdateObjCallback, game: Optional[Game]):
        users_all_desc = await self.accessor.get_all_users()

        if users_all_desc:
            table = "\n\n".join(
                [
                    "Игрок: {username}, игр: {total_games}, побед: {wins}, результативность: {efficiency}%".format(
                        username=user.username,
                        total_games=user.total_games,
                        wins=user.wins,
                        efficiency=user.efficiency * 100,
                    )
                    for user in users_all_desc
                ]
            )
            await self.message_queue.put(
                SendMessageObj(chat_id=game.chat_id, text=LEXICON_RU["statistics"].format(table=table))
            )
        else:
            await self.message_queue.put(SendMessageObj(chat_id=game.chat_id, text=LEXICON_RU["no statistics"]))

    async def handle_user_register_callback(self, update: UpdateObjCallback, game: Optional[Game]):
        if game.bot_state == REGISTRATION_STATE:
            message_id = update.callback_query.message.message_id
            user_id = update.callback_query.from_.id
            username = update.callback_query.from_.username
            first_name = update.callback_query.from_.first_name
            last_name = update.callback_query.from_.last_name

            profile_photos = await self.sender.tg_client.get_user_profile_photos(user_id=user_id, offset=0)

            if not profile_photos:
                await self.message_queue.put(
                    SendMessageObj(
                        chat_id=game.chat_id,
                        text=LEXICON_RU["no_user_profile_photo"].format(username=username),
                    )
                )
                return

            profile_photo_id = profile_photos[0][0].file_id
            await self.accessor.create_user_model_if_not_exists(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                profile_photo_id=profile_photo_id,
            )

            if user_id not in self.accessor.get_players_ids(players=game.players):
                await gather(
                    self.accessor.register_player(chat_id=game.chat_id, user_id=user_id),
                    self.message_queue.put(
                        EditMessageTextObj(
                            chat_id=game.chat_id,
                            message_id=message_id,
                            text=LEXICON_RU["registration"].format(players_num=len(game.accounts) + 1),
                            keyboard=REGISTRATION_KEYBOARD,
                        )
                    ),
                )

                # AnswerCallbackQueryObj(
                #     callback_query_id=update.callback_query.id,
                #     text=LEXICON_RU["user_register_answer"].format(username=username),
                # )

    async def handle_finish_registration_callback(self, update: UpdateObjCallback, game: Optional[Game]):
        if not self.accessor.can_players_start_game(game=game):
            await self.message_queue.put(
                SendMessageObj(chat_id=game.chat_id, text=LEXICON_RU["no_finish_registration"])
            )
            return

        await self.accessor.increment_users_total_games(game=game)  # who have registered
        await gather(
            self.accessor.change_current_bot_state(chat_id=game.chat_id, new_bot_state=GAMEPLAY_STATE),
            self.message_queue.put(
                SendMessageObj(
                    chat_id=game.chat_id,
                    text=LEXICON_RU["gameplay"],
                    keyboard=GAMEPLAY_KEYBOARD,
                )
            ),
        )

    async def handle_play_round_callback(self, update: UpdateObjCallback, game: Optional[Game]):
        message_id = update.callback_query.message.message_id
        # in case of timer mechanics:
        # current_round = game.current_round

        await gather(
            self.message_queue.put(
                EditMessageTextObj(
                    chat_id=game.chat_id,
                    message_id=message_id,
                    text=LEXICON_RU["start_round"],
                )
            ),
            self.accessor.change_current_bot_state(chat_id=game.chat_id, new_bot_state=START_ROUND_STATE),
        )

        player_first, player_second = sample(game.players, 2)  # User
        await gather(
            self.accessor.set_photo_num_for_selected_players(
                chat_id=game.chat_id, player_first=player_first, player_second=player_second
            ),
            *[
                self.message_queue.put(SendPhotoObj(chat_id=game.chat_id, photo=file_id, keyboard=photo_keyboard))
                for file_id, photo_keyboard in zip(
                    (player_first.profile_photo_id, player_second.profile_photo_id),
                    (FIRST_PHOTO_KEYBOARD, SECOND_PHOTO_KEYBOARD),
                )
            ],
            self.message_queue.put(
                SendMessageObj(chat_id=game.chat_id, text=LEXICON_RU["finish_round"], keyboard=FINISH_ROUND_KEYBOARD)
            ),
        )

        # in case of timer mechanics:
        # await sleep(30)
        # updated_game = await self.accessor.get_game_dataclass(chat_id=game.chat_id)  # Game
        # if updated_game.current_round == current_round:
        #     await self.choose_winner(game=updated_game)

    async def handle_first_photo_callback(self, update: UpdateObjCallback, game: Optional[Game]):
        if game.bot_state == START_ROUND_STATE:
            photo_num = FIRST_PHOTO
            await self.handle_photo_callback(update=update, game=game, photo_num=photo_num)

    async def handle_second_photo_callback(self, update: UpdateObjCallback, game: Optional[Game]):
        if game.bot_state == START_ROUND_STATE:
            photo_num = SECOND_PHOTO
            await self.handle_photo_callback(update=update, game=game, photo_num=photo_num)

    async def handle_photo_callback(self, update: UpdateObjCallback, game: Optional[Game], photo_num: str):
        user_id = update.callback_query.from_.id  # who voted

        if not self.accessor.can_player_vote(game=game, chat_id=game.chat_id, user_id=user_id):
            await self.message_queue.put(
                AnswerCallbackQueryObj(
                    callback_query_id=update.callback_query.id,
                    text=LEXICON_RU["no_chance_to_vote"],
                )
            )
            return

        await gather(
            self.message_queue.put(
                AnswerCallbackQueryObj(
                    callback_query_id=update.callback_query.id,
                    text=LEXICON_RU["success_vote"],
                )
            ),
            self.accessor.set_player_voted(chat_id=game.chat_id, user_id=user_id),  # for player who voted
        )
        await self.accessor.increment_player_score(game=game, photo_num=photo_num)  # for player who play in round

        updated_game = await self.accessor.get_game_dataclass(chat_id=game.chat_id)  # Game
        if self.accessor.are_all_players_vote(game=updated_game):
            await self.choose_winner(game=updated_game)

    async def handle_finish_round_callback(self, update: UpdateObjCallback, game: Optional[Game]):
        if game.bot_state == START_ROUND_STATE:
            await self.choose_winner(game=game)

    async def handle_next_round_callback(self, update: UpdateObjCallback, game: Optional[Game]):
        await self.accessor.reset_to_default_accounts_parameters(game=game)
        await gather(
            self.accessor.change_current_bot_state(chat_id=game.chat_id, new_bot_state=GAMEPLAY_STATE),
            self.message_queue.put(
                SendMessageObj(
                    chat_id=game.chat_id,
                    text=LEXICON_RU["gameplay"],
                    keyboard=GAMEPLAY_KEYBOARD,
                )
            ),
        )

    async def handle_exit_callback(self, update: UpdateObjCallback, game: Optional[Game]):
        await self.accessor.change_current_bot_state(chat_id=game.chat_id, new_bot_state=BEGINNING_STATE)
        # in case of timer mechanics:
        # await self.accessor.reset_current_round(chat_id=game.chat_id)
        await gather(
            self.accessor.delete_all_current_players(chat_id=game.chat_id),
            self.message_queue.put(
                SendMessageObj(
                    chat_id=game.chat_id,
                    text=LEXICON_RU["beginning"],
                    keyboard=BEGINNING_KEYBOARD,
                )
            ),
        )

    async def choose_winner(self, game: Optional[Game]):
        await self.accessor.change_current_bot_state(chat_id=game.chat_id, new_bot_state=FINISH_ROUND_STATE)
        # in case of timer mechanics:
        # await self.accessor.increment_current_round(game=game)
        winner_photo_num = await self.accessor.choose_winner_photo(game=game)

        updated_game = await self.accessor.get_game_dataclass(chat_id=game.chat_id)  # Game
        game_winner = self.accessor.get_whole_game_winner(game=updated_game)  # User

        if game_winner:
            await self.accessor.change_current_bot_state(chat_id=updated_game.chat_id, new_bot_state=BEGINNING_STATE)
            await self.accessor.increment_user_wins(user=game_winner)
            await self.send_game_winner_message(chat_id=updated_game.chat_id, winner=game_winner)
            await self.accessor.delete_all_current_players(chat_id=updated_game.chat_id)
            return

        await self.send_round_winner_message(chat_id=updated_game.chat_id, winner_photo_num=winner_photo_num)

    async def send_round_winner_message(self, chat_id: int, winner_photo_num: str):
        await gather(
            self.message_queue.put(SendMessageObj(chat_id=chat_id, text=LEXICON_RU[winner_photo_num])),
            self.message_queue.put(
                SendMessageObj(
                    chat_id=chat_id,
                    text=LEXICON_RU["next_round"],
                    keyboard=NEXT_ROUND_KEYBOARD,
                )
            ),
        )

    async def send_game_winner_message(self, chat_id: int, winner: User):
        await self.message_queue.put(
            SendMessageObj(
                chat_id=chat_id,
                text=LEXICON_RU["finish_game"].format(username=winner.username),
                keyboard=FINISH_GAME_KEYBOARD,
            )
        )

    async def stop(self):
        await self.update_queue.join()
        self.is_running = False

        for task in self._tasks:
            task.cancel()
            try:
                await task
            except CancelledError:
                print("task_work is cancelled")
