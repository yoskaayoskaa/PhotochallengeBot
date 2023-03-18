from bot.keyboard.lexicon_ru import LEXICON_RU
from bot.sender.dataclasses import InlineKeyboardButton, InlineKeyboardMarkup

START_REGISTRATION_CALLBACK = "start_registration_button"
STATISTICS_CALLBACK = "statistics_button"
USER_REGISTER_CALLBACK = "user_register_button"
FINISH_REGISTRATION_CALLBACK = "finish_registration_button"
PLAY_ROUND_CALLBACK = "play_round_button"
FIRST_PHOTO_CALLBACK = "first_photo_button"
SECOND_PHOTO_CALLBACK = "second_photo_button"
FINISH_ROUND_CALLBACK = "finish_round_button"
NEXT_ROUND_CALLBACK = "next_round_button"
EXIT_CALLBACK = "exit_button"

START_REGISTRATION_BUTTON = InlineKeyboardButton(
    text=LEXICON_RU["start_registration_button"],
    callback_data="start_registration_button",
)
STATISTICS_BUTTON = InlineKeyboardButton(text=LEXICON_RU["statistics_button"], callback_data="statistics_button")
USER_REGISTER_BUTTON = InlineKeyboardButton(
    text=LEXICON_RU["user_register_button"], callback_data="user_register_button"
)
FINISH_REGISTRATION_BUTTON = InlineKeyboardButton(
    text=LEXICON_RU["finish_registration_button"],
    callback_data="finish_registration_button",
)
PLAY_ROUND_BUTTON = InlineKeyboardButton(text=LEXICON_RU["play_round_button"], callback_data="play_round_button")
FIRST_PHOTO_BUTTON = InlineKeyboardButton(text=LEXICON_RU["first_photo_button"], callback_data="first_photo_button")
SECOND_PHOTO_BUTTON = InlineKeyboardButton(text=LEXICON_RU["second_photo_button"], callback_data="second_photo_button")
FINISH_ROUND_BUTTON = InlineKeyboardButton(text=LEXICON_RU["finish_round_button"], callback_data="finish_round_button")
NEXT_ROUND_BUTTON = InlineKeyboardButton(text=LEXICON_RU["next_round_button"], callback_data="next_round_button")
EXIT_BUTTON = InlineKeyboardButton(text=LEXICON_RU["exit_button"], callback_data="exit_button")

BEGINNING_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[[START_REGISTRATION_BUTTON], [STATISTICS_BUTTON]])
REGISTRATION_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [USER_REGISTER_BUTTON],
        [FINISH_REGISTRATION_BUTTON],
        [EXIT_BUTTON],
    ]
)
GAMEPLAY_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[[PLAY_ROUND_BUTTON], [EXIT_BUTTON]])
FIRST_PHOTO_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[[FIRST_PHOTO_BUTTON]])
SECOND_PHOTO_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[[SECOND_PHOTO_BUTTON]])
FINISH_ROUND_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[[FINISH_ROUND_BUTTON]])
NEXT_ROUND_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[[NEXT_ROUND_BUTTON], [EXIT_BUTTON]])
FINISH_GAME_KEYBOARD = InlineKeyboardMarkup(inline_keyboard=[[EXIT_BUTTON]])
