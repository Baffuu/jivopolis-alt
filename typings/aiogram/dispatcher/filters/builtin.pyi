"""
This type stub file was generated by pyright.
"""

import typing
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional, Union
from babel.support import LazyProxy
from aiogram import types
from aiogram.dispatcher.filters.filters import BoundFilter, Filter
from aiogram.types import BotCommand, CallbackQuery, ChatJoinRequest, ChatMemberUpdated, ChatType, InlineQuery, Message, Poll

ChatIDArgumentType = typing.Union[typing.Iterable[typing.Union[int, str]], str, int]
def extract_chat_ids(chat_id: ChatIDArgumentType) -> typing.Set[int]:
    ...

class Command(Filter):
    """
    You can handle commands by using this filter.

    If filter is successful processed the :obj:`Command.CommandObj` will be passed to the handler arguments.

    By default this filter is registered for messages and edited messages handlers.
    """
    def __init__(self, commands: Union[Iterable[Union[str, BotCommand]], str, BotCommand], prefixes: Union[Iterable, str] = ..., ignore_case: bool = ..., ignore_mention: bool = ..., ignore_caption: bool = ...) -> None:
        """
        Filter can be initialized from filters factory or by simply creating instance of this class.

        Examples:

        .. code-block:: python

            @dp.message_handler(commands=['myCommand'])
            @dp.message_handler(Command(['myCommand']))
            @dp.message_handler(commands=['myCommand'], commands_prefix='!/')

        :param commands: Command or list of commands always without leading slashes (prefix)
        :param prefixes: Allowed commands prefix. By default is slash.
            If you change the default behavior pass the list of prefixes to this argument.
        :param ignore_case: Ignore case of the command
        :param ignore_mention: Ignore mention in command
            (By default this filter pass only the commands addressed to current bot)
        :param ignore_caption: Ignore caption from message (in message types like photo, video, audio, etc)
            By default is True. If you want check commands in captions, you also should set required content_types.

            Examples:

            .. code-block:: python

                @dp.message_handler(commands=['myCommand'], commands_ignore_caption=False, content_types=ContentType.ANY)
                @dp.message_handler(Command(['myCommand'], ignore_caption=False), content_types=[ContentType.TEXT, ContentType.DOCUMENT])
        """
        ...
    
    @classmethod
    def validate(cls, full_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validator for filters factory

        From filters factory this filter can be registered with arguments:

         - ``command``
         - ``commands_prefix`` (will be passed as ``prefixes``)
         - ``commands_ignore_mention`` (will be passed as ``ignore_mention``)
         - ``commands_ignore_caption`` (will be passed as ``ignore_caption``)

        :param full_config:
        :return: config or empty dict
        """
        ...
    
    async def check(self, message: types.Message): # -> dict[str, CommandObj] | Literal[False]:
        ...
    
    @classmethod
    async def check_command(cls, message: types.Message, commands, prefixes, ignore_case=..., ignore_mention=..., ignore_caption=...): # -> dict[str, CommandObj] | Literal[False]:
        ...
    
    @dataclass
    class CommandObj:
        """
        Instance of this object is always has command and it prefix.

        Can be passed as keyword argument ``command`` to the handler
        """
        prefix: str = ...
        command: str = ...
        mention: str = ...
        args: str = ...
        @property
        def mentioned(self) -> bool:
            """
            This command has mention?

            :return:
            """
            ...
        
        @property
        def text(self) -> str:
            """
            Generate original text from object

            :return:
            """
            ...
        
    
    


class CommandStart(Command):
    """
    This filter based on :obj:`Command` filter but can handle only ``/start`` command.
    """
    def __init__(self, deep_link: typing.Optional[typing.Union[str, typing.Pattern[str]]] = ..., encoded: bool = ...) -> None:
        """
        Also this filter can handle `deep-linking <https://core.telegram.org/bots#deep-linking>`_ arguments.

        Example:

        .. code-block:: python

            @dp.message_handler(CommandStart(re.compile(r'ref-([\\d]+)')))

        :param deep_link: string or compiled regular expression (by ``re.compile(...)``).
        :param encoded: set True if you're waiting for encoded payload (default - False).
        """
        ...
    
    async def check(self, message: types.Message): # -> dict[str, str | None] | dict[str, Match[str]] | dict[str, CommandObj] | Literal[False]:
        """
        If deep-linking is passed to the filter result of the matching will be passed as ``deep_link`` to the handler

        :param message:
        :return:
        """
        ...
    


class CommandHelp(Command):
    """
    This filter based on :obj:`Command` filter but can handle only ``/help`` command.
    """
    def __init__(self) -> None:
        ...
    


class CommandSettings(Command):
    """
    This filter based on :obj:`Command` filter but can handle only ``/settings`` command.
    """
    def __init__(self) -> None:
        ...
    


class CommandPrivacy(Command):
    """
    This filter based on :obj:`Command` filter but can handle only ``/privacy`` command.
    """
    def __init__(self) -> None:
        ...
    


class Text(Filter):
    """
    Simple text filter
    """
    _default_params = ...
    def __init__(self, equals: Optional[Union[str, LazyProxy, Iterable[Union[str, LazyProxy]]]] = ..., contains: Optional[Union[str, LazyProxy, Iterable[Union[str, LazyProxy]]]] = ..., startswith: Optional[Union[str, LazyProxy, Iterable[Union[str, LazyProxy]]]] = ..., endswith: Optional[Union[str, LazyProxy, Iterable[Union[str, LazyProxy]]]] = ..., ignore_case=...) -> None:
        """
        Check text for one of pattern. Only one mode can be used in one filter.
        In every pattern, a single string is treated as a list with 1 element.

        :param equals: True if object's text in the list
        :param contains: True if object's text contains all strings from the list
        :param startswith: True if object's text starts with any of strings from the list
        :param endswith: True if object's text ends with any of strings from the list
        :param ignore_case: case insensitive
        """
        ...
    
    @classmethod
    def validate(cls, full_config: Dict[str, Any]): # -> dict[str, Any] | None:
        ...
    
    async def check(self, obj: Union[Message, CallbackQuery, InlineQuery, Poll]): # -> bool:
        ...
    


class HashTag(Filter):
    """
    Filter for hashtag's and cashtag's
    """
    def __init__(self, hashtags=..., cashtags=...) -> None:
        ...
    
    @classmethod
    def validate(cls, full_config: Dict[str, Any]): # -> dict[Unknown, Unknown]:
        ...
    
    async def check(self, message: types.Message): # -> dict[str, list[Unknown]] | Literal[False] | None:
        ...
    


class Regexp(Filter):
    """
    Regexp filter for messages and callback query
    """
    def __init__(self, regexp) -> None:
        ...
    
    @classmethod
    def validate(cls, full_config: Dict[str, Any]): # -> dict[str, Any] | None:
        ...
    
    async def check(self, obj: Union[Message, CallbackQuery, InlineQuery, Poll]): # -> dict[str, Match[str]] | Literal[False]:
        ...
    


class RegexpCommandsFilter(BoundFilter):
    """
    Check commands by regexp in message
    """
    key = ...
    def __init__(self, regexp_commands) -> None:
        ...
    
    async def check(self, message): # -> dict[str, Match[str]] | Literal[False]:
        ...
    


class ContentTypeFilter(BoundFilter):
    """
    Check message content type
    """
    key = ...
    required = ...
    default = ...
    def __init__(self, content_types) -> None:
        ...
    
    async def check(self, message): # -> bool:
        ...
    


class IsSenderContact(BoundFilter):
    """
    Filter check that the contact matches the sender

    `is_sender_contact=True` - contact matches the sender
    `is_sender_contact=False` - result will be inverted
    """
    key = ...
    def __init__(self, is_sender_contact: bool) -> None:
        ...
    
    async def check(self, message: types.Message) -> bool:
        ...
    


class StateFilter(BoundFilter):
    """
    Check user state
    """
    key = ...
    required = ...
    ctx_state = ...
    def __init__(self, dispatcher, state) -> None:
        ...
    
    def get_target(self, obj): # -> tuple[Any | None, Any | None]:
        ...
    
    async def check(self, obj): # -> dict[str, Unknown] | Literal[False]:
        ...
    


class ExceptionsFilter(BoundFilter):
    """
    Filter for exceptions
    """
    key = ...
    def __init__(self, exception) -> None:
        ...
    
    async def check(self, update, exception): # -> bool:
        ...
    


class IDFilter(Filter):
    def __init__(self, user_id: Optional[ChatIDArgumentType] = ..., chat_id: Optional[ChatIDArgumentType] = ...) -> None:
        """
        :param user_id:
        :param chat_id:
        """
        ...
    
    @classmethod
    def validate(cls, full_config: typing.Dict[str, typing.Any]) -> typing.Optional[typing.Dict[str, typing.Any]]:
        ...
    
    async def check(self, obj: Union[Message, CallbackQuery, InlineQuery, ChatMemberUpdated, ChatJoinRequest]): # -> bool:
        ...
    


class AdminFilter(Filter):
    """
    Checks if user is admin in a chat.
    If is_chat_admin is not set, the filter will check in the current chat (correct only for messages).
    is_chat_admin is required for InlineQuery.
    """
    def __init__(self, is_chat_admin: Optional[Union[ChatIDArgumentType, bool]] = ...) -> None:
        ...
    
    @classmethod
    def validate(cls, full_config: typing.Dict[str, typing.Any]) -> typing.Optional[typing.Dict[str, typing.Any]]:
        ...
    
    async def check(self, obj: Union[Message, CallbackQuery, InlineQuery, ChatMemberUpdated]) -> bool:
        ...
    


class IsReplyFilter(BoundFilter):
    """
    Check if message is replied and send reply message to handler
    """
    key = ...
    def __init__(self, is_reply) -> None:
        ...
    
    async def check(self, msg: Message): # -> dict[str, Message] | Literal[True] | None:
        ...
    


class ForwardedMessageFilter(BoundFilter):
    key = ...
    def __init__(self, is_forwarded: bool) -> None:
        ...
    
    async def check(self, message: Message): # -> bool:
        ...
    


class ChatTypeFilter(BoundFilter):
    key = ...
    def __init__(self, chat_type: typing.Container[ChatType]) -> None:
        ...
    
    async def check(self, obj: Union[Message, CallbackQuery, ChatMemberUpdated, InlineQuery]): # -> bool:
        ...
    


class MediaGroupFilter(BoundFilter):
    """
    Check if message is part of a media group.

    `is_media_group=True` - the message is part of a media group
    `is_media_group=False` - the message is NOT part of a media group
    """
    key = ...
    def __init__(self, is_media_group: bool) -> None:
        ...
    
    async def check(self, message: types.Message) -> bool:
        ...
    

