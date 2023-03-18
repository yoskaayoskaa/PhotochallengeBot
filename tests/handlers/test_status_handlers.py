from typing import Optional

from bot.general import TgBot
from bot.models import Game
from bot.poller.dataclasses import UpdateObjMyChatMember
from bot.worker.fsm import BEGINNING_STATE, DELETED_STATE


class TestStatusHandlers:
    async def test_status_member_no_game(self, tg_bot: TgBot, update_status_member: UpdateObjMyChatMember):
        updated_game = await self._get_updated_game(
            bot=tg_bot,
            handler=tg_bot.worker.handle_status_member_update,
            update=update_status_member,
        )

        assert updated_game is not None
        assert updated_game.bot_state == BEGINNING_STATE
        assert updated_game.players == []
        assert updated_game.accounts == []

    async def test_status_member_with_game(
        self, tg_bot: TgBot, update_status_member: UpdateObjMyChatMember, game_no_players: Game
    ):
        updated_game = await self._get_updated_game(
            bot=tg_bot,
            handler=tg_bot.worker.handle_status_member_update,
            update=update_status_member,
            game=game_no_players,
        )

        assert updated_game is not None
        assert updated_game.bot_state == BEGINNING_STATE
        assert updated_game.players == []
        assert updated_game.accounts == []

    async def test_status_left(self, tg_bot: TgBot, update_status_member: UpdateObjMyChatMember, game_one_player: Game):
        update_status_member.my_chat_member.new_chat_member.status = "left"
        updated_game = await self._get_updated_game(
            bot=tg_bot,
            handler=tg_bot.worker.handle_status_left_update,
            update=update_status_member,
            game=game_one_player,
        )

        assert updated_game is not None
        assert updated_game.bot_state == DELETED_STATE
        assert updated_game.players == []
        assert updated_game.accounts == []

    @staticmethod
    async def _get_updated_game(
        bot: TgBot,
        handler: classmethod,
        update: UpdateObjMyChatMember,
        game: Optional[Game] = None,
    ) -> Optional[Game]:
        chat_id = update.my_chat_member.chat.id
        await handler(update=update, game=game)
        return await bot.worker.accessor.get_game_dataclass(chat_id=chat_id)
