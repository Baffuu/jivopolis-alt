"""
This type stub file was generated by pyright.
"""

import typing
from . import base
from .callback_game import CallbackGame
from .login_url import LoginUrl
from .web_app_info import WebAppInfo

class InlineKeyboardMarkup(base.TelegramObject):
    """
    This object represents an inline keyboard that appears right next to the message it belongs to.

    Note: This will only work in Telegram versions released after 9 April, 2016.
    Older clients will display unsupported message.

    https://core.telegram.org/bots/api#inlinekeyboardmarkup
    """
    inline_keyboard: typing.List[typing.List[InlineKeyboardButton]] = ...
    def __init__(self, row_width=..., inline_keyboard=..., **kwargs) -> None:
        ...
    
    @property
    def row_width(self): # -> Any | int:
        ...
    
    @row_width.setter
    def row_width(self, value): # -> None:
        ...
    
    def add(self, *args): # -> Self@InlineKeyboardMarkup:
        """
        Add buttons

        :param args:
        :return: self
        :rtype: :obj:`types.InlineKeyboardMarkup`
        """
        ...
    
    def row(self, *buttons): # -> Self@InlineKeyboardMarkup:
        """
        Add row

        :param buttons:
        :return: self
        :rtype: :obj:`types.InlineKeyboardMarkup`
        """
        ...
    
    def insert(self, button): # -> Self@InlineKeyboardMarkup:
        """
        Insert button to last row

        :param button:
        :return: self
        :rtype: :obj:`types.InlineKeyboardMarkup`
        """
        ...
    


class InlineKeyboardButton(base.TelegramObject):
    """
    This object represents one button of an inline keyboard. You must use exactly one of the optional fields.

    https://core.telegram.org/bots/api#inlinekeyboardbutton
    """
    text: base.String = ...
    url: base.String = ...
    login_url: LoginUrl = ...
    callback_data: base.String = ...
    switch_inline_query: base.String = ...
    switch_inline_query_current_chat: base.String = ...
    callback_game: CallbackGame = ...
    pay: base.Boolean = ...
    web_app: WebAppInfo = ...
    def __init__(self, text: base.String, url: base.String = ..., login_url: LoginUrl = ..., callback_data: base.String = ..., switch_inline_query: base.String = ..., switch_inline_query_current_chat: base.String = ..., callback_game: CallbackGame = ..., pay: base.Boolean = ..., web_app: WebAppInfo = ..., **kwargs) -> None:
        ...
    

