"""
This type stub file was generated by pyright.
"""

import typing
from . import base
from ..utils import helper

class BotCommandScopeType(helper.Helper):
    mode = ...
    DEFAULT = ...
    ALL_PRIVATE_CHATS = ...
    ALL_GROUP_CHATS = ...
    ALL_CHAT_ADMINISTRATORS = ...
    CHAT = ...
    CHAT_ADMINISTRATORS = ...
    CHAT_MEMBER = ...


class BotCommandScope(base.TelegramObject):
    """
    This object represents the scope to which bot commands are applied.
    Currently, the following 7 scopes are supported:
        BotCommandScopeDefault
        BotCommandScopeAllPrivateChats
        BotCommandScopeAllGroupChats
        BotCommandScopeAllChatAdministrators
        BotCommandScopeChat
        BotCommandScopeChatAdministrators
        BotCommandScopeChatMember

    https://core.telegram.org/bots/api#botcommandscope
    """
    type: base.String = ...
    @classmethod
    def from_type(cls, type: str, **kwargs: typing.Any): # -> BotCommandScopeDefault | BotCommandScopeAllPrivateChats | BotCommandScopeAllGroupChats | BotCommandScopeAllChatAdministrators | BotCommandScopeChat | BotCommandScopeChatAdministrators | BotCommandScopeChatMember:
        ...
    


class BotCommandScopeDefault(BotCommandScope):
    """
    Represents the default scope of bot commands.
    Default commands are used if no commands with a narrower scope are
    specified for the user.
    """
    type = ...


class BotCommandScopeAllPrivateChats(BotCommandScope):
    """
    Represents the scope of bot commands, covering all private chats.
    """
    type = ...


class BotCommandScopeAllGroupChats(BotCommandScope):
    """
    Represents the scope of bot commands, covering all group and
    supergroup chats.
    """
    type = ...


class BotCommandScopeAllChatAdministrators(BotCommandScope):
    """
    Represents the scope of bot commands, covering all group and
    supergroup chat administrators.
    """
    type = ...


class BotCommandScopeChat(BotCommandScope):
    """
    Represents the scope of bot commands, covering a specific chat.
    """
    type = ...
    chat_id: typing.Union[base.String, base.Integer] = ...
    def __init__(self, chat_id: typing.Union[base.String, base.Integer], **kwargs) -> None:
        ...
    


class BotCommandScopeChatAdministrators(BotCommandScopeChat):
    """
    Represents the scope of bot commands, covering all administrators
    of a specific group or supergroup chat.
    """
    type = ...
    chat_id: typing.Union[base.String, base.Integer] = ...


class BotCommandScopeChatMember(BotCommandScopeChat):
    """
    Represents the scope of bot commands, covering a specific member of
    a group or supergroup chat.
    """
    type = ...
    chat_id: typing.Union[base.String, base.Integer] = ...
    user_id: base.Integer = ...
    def __init__(self, chat_id: typing.Union[base.String, base.Integer], user_id: base.Integer, **kwargs) -> None:
        ...
    

