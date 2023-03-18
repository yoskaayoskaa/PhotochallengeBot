import decimal
from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy import BIGINT, Boolean, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from bot.worker.fsm import BEGINNING_STATE
from database.sqlalchemy_base import db


@dataclass
class Account:
    user_id: int
    game_id: int
    vote: bool
    scores: int
    photo_num: str


@dataclass
class User:
    id: int
    username: str
    profile_photo_id: str
    wins: int
    total_games: int
    efficiency: decimal
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@dataclass
class Game:
    chat_id: int
    bot_state: str
    current_round: int
    players: List[Optional[User]]
    accounts: List[Optional[Account]]


class AccountModel(db):
    __tablename__ = "accounts"

    user_id = Column(ForeignKey("users.id"), primary_key=True)
    game_id = Column(ForeignKey("games.chat_id"), primary_key=True)
    vote = Column(Boolean, default=False, nullable=False)
    scores = Column(Integer, default=0, nullable=False)
    photo_num = Column(String, default="no", nullable=False)

    def __repr__(self):
        return f"AccountModel(user_id={self.user_id}, game_id={self.game_id})"

    @property
    def dataclass(self) -> Account:
        return Account(
            user_id=self.user_id,
            game_id=self.game_id,
            vote=self.vote,
            scores=self.scores,
            photo_num=self.photo_num,
        )


class UserModel(db):
    __tablename__ = "users"

    id = Column(BIGINT, primary_key=True, unique=True, autoincrement=False)
    username = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    profile_photo_id = Column(String)  # file_id
    wins = Column(Integer, default=0, nullable=False)
    total_games = Column(Integer, default=0, nullable=False)
    efficiency = Column(Numeric(precision=3, scale=2, asdecimal=True), default=0, nullable=False)

    games = relationship("GameModel", secondary="accounts", back_populates="players")

    def __repr__(self):
        return f"UserModel(id={self.id}, username={self.username})"

    @property
    def dataclass(self) -> User:
        return User(
            id=self.id,
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            profile_photo_id=self.profile_photo_id,
            wins=self.wins,
            total_games=self.total_games,
            efficiency=self.efficiency,
        )


class GameModel(db):
    __tablename__ = "games"  # один чат - одна игра

    chat_id = Column(BIGINT, primary_key=True, unique=True, autoincrement=False)
    bot_state = Column(String, default=BEGINNING_STATE, nullable=False)
    current_round = Column(Integer, default=1, nullable=False)

    players = relationship("UserModel", secondary="accounts", back_populates="games")

    def __repr__(self):
        return f"GameModel(chat={self.chat_id}, bot_state={self.bot_state})"

    def transform_to_dataclass(self, accounts: List[Optional[Account]]) -> Game:
        return Game(
            chat_id=self.chat_id,
            bot_state=self.bot_state,
            current_round=self.current_round,
            players=[player.dataclass for player in self.players],
            accounts=accounts,
        )


class AdminModel(db):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, unique=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)  # password_hash

    def __repr__(self):
        return f"AdminModel(id={self.id}, email={self.email})"
