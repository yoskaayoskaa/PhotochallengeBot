import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from bot.models import AccountModel, Game, GameModel, User, UserModel
from bot.worker.status import FIRST_PHOTO, SECOND_PHOTO


@pytest.fixture
async def user_1(db_session: async_sessionmaker) -> User:
    new_user_1 = UserModel(
        id=242360,
        username="user_1",
        profile_photo_id="file_id_1",
        wins=0,
        total_games=1,
        efficiency=0.00,
    )
    async with db_session.begin() as session:
        session.add(new_user_1)

    return new_user_1.dataclass


@pytest.fixture
async def user_2(db_session: async_sessionmaker) -> User:
    new_user_2 = UserModel(
        id=2,
        username="user_2",
        profile_photo_id="file_id_2",
        wins=0,
        total_games=1,
        efficiency=0.00,
    )
    async with db_session.begin() as session:
        session.add(new_user_2)

    return new_user_2.dataclass


@pytest.fixture
async def game_no_players(db_session: async_sessionmaker) -> Game:
    game_no_players = GameModel(chat_id=-123, bot_state="no_state", current_round=1)
    async with db_session.begin() as session:
        session.add(game_no_players)

    return Game(
        chat_id=game_no_players.chat_id,
        bot_state=game_no_players.bot_state,
        current_round=game_no_players.current_round,
        players=[],
        accounts=[],
    )


@pytest.fixture
async def game_one_player(db_session: async_sessionmaker, game_no_players: Game, user_1: User) -> Game:
    new_account_1 = AccountModel(
        user_id=user_1.id, game_id=game_no_players.chat_id, vote=False, scores=0, photo_num="no"
    )
    async with db_session.begin() as session:
        session.add(new_account_1)

    return Game(
        chat_id=game_no_players.chat_id,
        bot_state=game_no_players.bot_state,
        current_round=game_no_players.current_round,
        players=[user_1],
        accounts=[new_account_1.dataclass],
    )


@pytest.fixture
async def game_two_players(db_session: async_sessionmaker, game_no_players: Game, user_1: User, user_2: User) -> Game:
    new_account_1 = AccountModel(
        user_id=user_1.id, game_id=game_no_players.chat_id, vote=False, scores=0, photo_num="no"
    )
    new_account_2 = AccountModel(
        user_id=user_2.id, game_id=game_no_players.chat_id, vote=False, scores=0, photo_num="no"
    )
    return await get_game_two_players(
        db_session=db_session,
        game=game_no_players,
        user_1=user_1,
        user_2=user_2,
        account_1=new_account_1,
        account_2=new_account_2,
    )


@pytest.fixture
async def game_two_players_round(
    db_session: async_sessionmaker, game_no_players: Game, user_1: User, user_2: User
) -> Game:
    new_account_1 = AccountModel(
        user_id=user_1.id, game_id=game_no_players.chat_id, vote=False, scores=0, photo_num=FIRST_PHOTO
    )
    new_account_2 = AccountModel(
        user_id=user_2.id, game_id=game_no_players.chat_id, vote=True, scores=1, photo_num=SECOND_PHOTO
    )
    return await get_game_two_players(
        db_session=db_session,
        game=game_no_players,
        user_1=user_1,
        user_2=user_2,
        account_1=new_account_1,
        account_2=new_account_2,
    )


async def get_game_two_players(
    db_session: async_sessionmaker,
    game: Game,
    user_1: User,
    user_2: User,
    account_1: AccountModel,
    account_2: AccountModel,
) -> Game:
    async with db_session.begin() as session:
        session.add_all([account_1, account_2])

    return Game(
        chat_id=game.chat_id,
        bot_state=game.bot_state,
        current_round=game.current_round,
        players=[user_1, user_2],
        accounts=[account_1.dataclass, account_2.dataclass],
    )
