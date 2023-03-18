from typing import Optional

from bot.general import TgBot
from bot.models import Game
from bot.poller.dataclasses import UpdateObjCallback
from bot.worker.fsm import BEGINNING_STATE, GAMEPLAY_STATE, REGISTRATION_STATE, START_ROUND_STATE
from bot.worker.status import FIRST_PHOTO, SECOND_PHOTO


class TestCallbacksHandlers:
    async def test_start_registration_callback(
        self, tg_bot: TgBot, update_callback: UpdateObjCallback, game_no_players: Game
    ):
        updated_game = await self._get_updated_game(
            bot=tg_bot,
            handler=tg_bot.worker.handle_start_registration_callback,
            update=update_callback,
            game=game_no_players,
        )

        assert updated_game is not None
        assert updated_game.bot_state == REGISTRATION_STATE

    async def test_user_register_callback(
        self, tg_bot: TgBot, update_callback: UpdateObjCallback, game_no_players: Game
    ):
        game_no_players.bot_state = REGISTRATION_STATE
        updated_game = await self._get_updated_game(
            bot=tg_bot,
            handler=tg_bot.worker.handle_user_register_callback,
            update=update_callback,
            game=game_no_players,
        )

        assert updated_game is not None
        assert updated_game.players != []
        assert updated_game.accounts != []
        assert updated_game.players[0].id == update_callback.callback_query.from_.id
        assert updated_game.accounts[0].game_id == update_callback.callback_query.message.chat.id
        assert updated_game.accounts[0].user_id == update_callback.callback_query.from_.id

    async def test_finish_registration_callback(
        self, tg_bot: TgBot, update_callback: UpdateObjCallback, game_two_players: Game
    ):
        updated_game = await self._get_updated_game(
            bot=tg_bot,
            handler=tg_bot.worker.handle_finish_registration_callback,
            update=update_callback,
            game=game_two_players,
        )

        assert updated_game is not None
        assert len(updated_game.players) == 2
        assert len(updated_game.accounts) == 2
        assert updated_game.players[0].total_games == updated_game.players[1].total_games == 2
        assert updated_game.bot_state == GAMEPLAY_STATE

    async def test_play_round_callback(self, tg_bot: TgBot, update_callback: UpdateObjCallback, game_two_players: Game):
        updated_game = await self._get_updated_game(
            bot=tg_bot,
            handler=tg_bot.worker.handle_play_round_callback,
            update=update_callback,
            game=game_two_players,
        )

        assert updated_game is not None
        assert updated_game.bot_state == START_ROUND_STATE
        assert all(map(lambda account: account.photo_num in (FIRST_PHOTO, SECOND_PHOTO), updated_game.accounts))

    async def test_second_photo_callback(
        self, tg_bot: TgBot, update_callback: UpdateObjCallback, game_two_players_round: Game
    ):
        game_two_players_round.bot_state = START_ROUND_STATE
        updated_game = await self._get_updated_game(
            bot=tg_bot,
            handler=tg_bot.worker.handle_second_photo_callback,
            update=update_callback,
            game=game_two_players_round,
        )
        winner = tuple(filter(lambda user: user.id == 2, await tg_bot.worker.accessor.get_all_users()))[0]

        assert updated_game is not None
        assert updated_game.bot_state == BEGINNING_STATE
        assert winner is not None
        assert winner.wins == 1
        assert updated_game.accounts == []

    async def test_next_round_callback(
        self, tg_bot: TgBot, update_callback: UpdateObjCallback, game_two_players_round: Game
    ):
        updated_game = await self._get_updated_game(
            bot=tg_bot,
            handler=tg_bot.worker.handle_next_round_callback,
            update=update_callback,
            game=game_two_players_round,
        )

        assert updated_game is not None
        assert updated_game.bot_state == GAMEPLAY_STATE
        assert all(
            map(
                lambda account: all((not account.vote, account.scores == 0, account.photo_num == "no")),
                updated_game.accounts,
            )
        )

    async def test_exit_callback(self, tg_bot: TgBot, update_callback: UpdateObjCallback, game_two_players: Game):
        updated_game = await self._get_updated_game(
            bot=tg_bot,
            handler=tg_bot.worker.handle_exit_callback,
            update=update_callback,
            game=game_two_players,
        )

        assert updated_game is not None
        assert updated_game.bot_state == BEGINNING_STATE
        assert updated_game.players == []
        assert updated_game.accounts == []

    @staticmethod
    async def _get_updated_game(
        bot: TgBot,
        handler: classmethod,
        update: UpdateObjCallback,
        game: Optional[Game] = None,
    ) -> Optional[Game]:
        chat_id = update.callback_query.message.chat.id
        await handler(update=update, game=game)
        return await bot.worker.accessor.get_game_dataclass(chat_id=chat_id)
