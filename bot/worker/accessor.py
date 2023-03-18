from typing import List, Optional

from sqlalchemy import delete, desc, insert, select, update
from sqlalchemy.dialects.postgresql import insert as pg_upsert
from sqlalchemy.orm import selectinload

from bot.models import Account, AccountModel, Game, GameModel, User, UserModel
from bot.worker.fsm import BEGINNING_STATE
from bot.worker.status import FIRST_PHOTO, SECOND_PHOTO
from database.database import Database


class BotAccessor:
    def __init__(self, database: Database):
        self.database = database

    async def create_user_model_if_not_exists(
        self,
        user_id: int,
        username: str,
        first_name: str,
        last_name: str,
        profile_photo_id: str,
    ) -> None:
        statement = pg_upsert(UserModel).values(
            id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            profile_photo_id=profile_photo_id,
        )
        do_update_statement = statement.on_conflict_do_update(
            index_elements=["id"],
            set_=dict(
                username=username,
                first_name=first_name,
                last_name=last_name,
                profile_photo_id=profile_photo_id,
            ),
        )
        await self.database.execute_statement(statement=do_update_statement)

    async def create_game_model(self, chat_id: int) -> None:
        statement = insert(GameModel).values(chat_id=chat_id, bot_state=BEGINNING_STATE)
        await self.database.execute_statement(statement=statement)

    async def register_player(self, chat_id: int, user_id: int) -> None:
        statement = insert(AccountModel).values(user_id=user_id, game_id=chat_id)
        await self.database.execute_statement(statement=statement)

    async def set_photo_num_for_selected_players(self, chat_id: int, player_first: User, player_second: User) -> None:
        for photo_num, player in zip((FIRST_PHOTO, SECOND_PHOTO), (player_first, player_second)):
            statement = (
                update(AccountModel)
                .where(AccountModel.game_id == chat_id, AccountModel.user_id == player.id)
                .values(photo_num=photo_num)
            )
            await self.database.execute_statement(statement=statement)

    async def set_player_voted(self, chat_id: int, user_id: int) -> None:
        statement = (
            update(AccountModel)
            .where(AccountModel.user_id == user_id, AccountModel.game_id == chat_id)
            .values(vote=True)
        )
        await self.database.execute_statement(statement=statement)

    async def increment_player_score(self, game: Game, photo_num: str) -> None:
        player_account = tuple(
            filter(
                lambda account: account.game_id == game.chat_id and account.photo_num == photo_num,
                game.accounts,
            )
        )[0]

        statement = (
            update(AccountModel)
            .where(
                AccountModel.game_id == game.chat_id,
                AccountModel.photo_num == photo_num,
            )
            .values(scores=player_account.scores + 1)
        )
        await self.database.execute_statement(statement=statement)

    async def choose_winner_photo(self, game: Game) -> str:
        round_players_accounts = sorted(
            filter(lambda account: account.photo_num != "no", game.accounts),
            key=lambda account: account.scores,
        )
        looser, winner = round_players_accounts[0], round_players_accounts[1]

        if looser.scores == winner.scores:
            return "draw"

        await self.remove_looser_from_players(looser=looser)
        return winner.photo_num

    async def remove_looser_from_players(self, looser: Account) -> None:
        statement = delete(AccountModel).where(
            AccountModel.user_id == looser.user_id,
            AccountModel.game_id == looser.game_id,
        )
        await self.database.execute_statement(statement=statement)

    async def reset_to_default_accounts_parameters(self, game: Game) -> None:
        for account in game.accounts:
            statement = (
                update(AccountModel)
                .where(
                    AccountModel.user_id == account.user_id,
                    AccountModel.game_id == account.game_id,
                )
                .values(vote=False, scores=0, photo_num="no")
            )
            await self.database.execute_statement(statement=statement)

    async def increment_users_total_games(self, game: Game) -> None:
        for user in game.players:
            statement = update(UserModel).where(UserModel.id == user.id).values(total_games=user.total_games + 1)
            await self.database.execute_statement(statement=statement)

    async def increment_user_wins(self, user: User) -> None:
        statement = (
            update(UserModel)
            .where(UserModel.id == user.id)
            .values(wins=user.wins + 1, efficiency=(user.wins + 1) / user.total_games)
        )
        await self.database.execute_statement(statement=statement)

    async def delete_all_current_players(self, chat_id: int) -> None:
        statement = delete(AccountModel).where(AccountModel.game_id == chat_id)
        await self.database.execute_statement(statement=statement)

    async def change_current_bot_state(self, chat_id: int, new_bot_state: str) -> None:
        statement = update(GameModel).where(GameModel.chat_id == chat_id).values(bot_state=new_bot_state)
        await self.database.execute_statement(statement=statement)

    async def increment_current_round(self, game: Game) -> None:
        statement = (
            update(GameModel).where(GameModel.chat_id == game.chat_id).values(current_round=game.current_round + 1)
        )
        await self.database.execute_statement(statement=statement)

    async def reset_current_round(self, chat_id: int) -> None:
        statement = update(GameModel).where(GameModel.chat_id == chat_id).values(current_round=1)
        await self.database.execute_statement(statement=statement)

    async def get_game_dataclass(self, chat_id: int) -> Optional[Game]:
        statement_game = select(GameModel).where(GameModel.chat_id == chat_id).options(selectinload(GameModel.players))
        game_models_list = await self.database.execute_statement_scalars(statement=statement_game)

        statement_account = select(AccountModel).where(AccountModel.game_id == chat_id)
        account_models_list = await self.database.execute_statement_scalars(statement=statement_account)
        accounts = [account_model.dataclass for account_model in account_models_list]

        return game_models_list[0].transform_to_dataclass(accounts=accounts) if game_models_list else None

    async def get_all_users(self) -> List[Optional[User]]:
        statement = select(UserModel).order_by(desc(UserModel.efficiency))
        user_models_list = await self.database.execute_statement_scalars(statement=statement)

        return [user_model.dataclass for user_model in user_models_list]

    def can_player_vote(self, game: Game, chat_id: int, user_id: int) -> bool:
        if user_id not in self.get_players_ids(players=game.players):
            return False

        player_account = tuple(
            filter(
                lambda account: account.user_id == user_id and account.game_id == chat_id,
                game.accounts,
            )
        )[0]
        return not player_account.vote

    @staticmethod
    def get_players_ids(players: list) -> List[int]:
        return [player.id for player in players]

    @staticmethod
    def can_players_start_game(game: Game) -> bool:
        players_num = len(game.players)
        return all((players_num % 2 == 0, players_num > 0))

    @staticmethod
    def are_all_players_vote(game: Game) -> bool:
        who_votes = tuple(filter(lambda account: account.vote, game.accounts))
        return len(who_votes) == len(game.accounts)

    @staticmethod
    def get_whole_game_winner(game: Game) -> Optional[User]:
        return game.players[0] if len(game.players) == 1 else None
