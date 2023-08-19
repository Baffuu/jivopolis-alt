from .. import bot
from ..database.functions import current_time
from aiogram.types import (
    Message, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
)
import re


async def can_perform(user_id: int, other_id: int, chat_id: int | str,
                      right: str) -> bool:
    '''
    Returns True if user_id is allowed to perform some action upon other

    :param user_id - supposed moderator id:
    :param other_id - target id:
    :param chat_id - chat id:
    :param right - a right to be checked:
    '''
    member = await bot.get_chat_member(chat_id, user_id)
    other = await bot.get_chat_member(chat_id, other_id)
    if not (member.is_chat_owner() or member.is_chat_admin()):
        return False
    elif other.is_chat_owner() or (other.is_chat_admin() and
                                   right != 'can_promote_members'):
        return False
    else:
        return member[right]


def decode_term(string_term: str) -> int | str:
    '''
    Returns amount of seconds from string

    :param string_term - string interpretation of term:
    '''
    if string_term != "forever":
        try:
            temporary_value = int(string_term if string_term[-1].isnumeric()
                                  else string_term[:-1])
        except Exception:
            return "not int"
    if string_term[-1].isnumeric():
        temporary_value = int(string_term) * 60
    elif string_term == "forever":
        return 31622500
    else:
        match(string_term[-1]):
            case 's':
                multiplier = 1
            case 'h':
                multiplier = 3600
            case 'd':
                multiplier = 86400
            case 'w':
                multiplier = 604800
            case _:
                multiplier = 60
        temporary_value *= multiplier

    if temporary_value < 35 or temporary_value > 31622399:
        return "incorrect term"
    else:
        return temporary_value


async def mute_member(message: Message) -> None:
    '''
    Mute chat member.

    :param message - moderator's message:
    '''
    user_id = message.from_user.id
    markup = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(
                    text="🥱 Понятно",
                    callback_data="cancel_action"
                )
            )
    other_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id

    if not await can_perform(user_id, other_id, chat_id,
                             'can_restrict_members'):
        return await message.reply(
            '😨 <i>У вас нет прав на выполнение этого действия</i>',
            reply_markup=markup
        )

    if message.text:
        term_identifier = message.text.replace(" ", "").replace("!mute", "")
        seconds = decode_term(term_identifier) if term_identifier else 300
        if seconds == "not int":
            return await message.reply(
                '😨 <i>Срок мута должен быть записан в одном из следующих '
                'форматов:\n\n<code>{целое_количество_минут}</code>\n\n<code>'
                '{целое_число}{s|h|d|w}</code>\n\n<code>forever</code></i>',
                reply_markup=markup
            )
        elif seconds == "incorrect term":
            return await message.reply(
                '😨 <i>Срок мута должен быть больше 35 секунд и меньше 1 года. '
                'Если вы хотите заглушить пользователя навсегда, используйте '
                'команду <code>/mute forever</code></i>',
                reply_markup=markup
            )

        if not term_identifier:
            str_term = "5 минут"
        elif term_identifier[-1].isnumeric():
            str_term = f"{term_identifier} минут"
        elif term_identifier == "forever":
            str_term = "неопределённый срок"
        else:
            match(term_identifier[-1]):
                case "s":
                    units = "секунд"
                case "h":
                    units = "часов"
                case "d":
                    units = "дней"
                case "w":
                    units = "недель"
                case _:
                    units = "минут"
            str_term = f"{term_identifier[:-1]} {units}"
    else:
        seconds = 300
        str_term = "5 минут"

    try:
        await bot.restrict_chat_member(chat_id, other_id,
                                       ChatPermissions(False),
                                       until_date=current_time()+seconds)
        await message.reply_to_message.reply(
            f'😣 <i>Вы были заглушены на <b>{str_term}</b></i>'
        )
    except Exception:
        return await message.reply(
            '😨 <i>Произошла ошибка. Возможно, у Живополиса недостаточно'
            ' прав</i>',
            reply_markup=markup
        )


async def unmute_member(message: Message) -> None:
    '''
    Unmute chat member.

    :param message - moderator's message:
    '''
    user_id = message.from_user.id
    markup = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(
                    text="🥱 Понятно",
                    callback_data="cancel_action"
                )
            )
    other_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id

    if not await can_perform(user_id, other_id, chat_id,
                             'can_restrict_members'):
        return await message.reply(
            '😨 <i>У вас нет прав на выполнение этого действия</i>',
            reply_markup=markup
        )

    try:
        permissions = ChatPermissions(
            *[True for i in range(8)]
        )
        await bot.restrict_chat_member(chat_id, other_id,
                                       permissions)
        await message.reply_to_message.reply(
            '🥳 <i>Вы снова можете говорить</i>'
        )
    except Exception:
        return await message.reply(
            '😨 <i>Произошла ошибка. Возможно, у Живополиса недостаточно'
            ' прав</i>',
            reply_markup=markup
        )


async def demote_member(message: Message) -> None:
    '''
    Demote chat member.

    :param message - moderator's message:
    '''
    user_id = message.from_user.id
    markup = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(
                    text="🥱 Понятно",
                    callback_data="cancel_action"
                )
            )
    other_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id

    if not await can_perform(user_id, other_id, chat_id,
                             'can_promote_members'):
        return await message.reply(
            '😨 <i>У вас нет прав на выполнение этого действия</i>',
            reply_markup=markup
        )

    try:
        await bot.promote_chat_member(
            chat_id, other_id, False, False)
        await message.reply_to_message.reply(
            '😪 <i>Вы больше не админ :(</i>'
        )
    except Exception:
        return await message.reply(
            '😨 <i>Произошла ошибка. Возможно, у Живополиса недостаточно'
            ' прав</i>',
            reply_markup=markup
        )


async def promote_member(message: Message, title_only: bool = False) -> None:
    '''
    Promote chat member.

    :param message - moderator's message:
    :param title_only - True if no rights should be given to the member:
    '''
    user_id = message.from_user.id
    markup = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(
                    text="🥱 Понятно",
                    callback_data="cancel_action"
                )
            )
    other_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id

    if not await can_perform(user_id, other_id, chat_id,
                             'can_promote_members'):
        return await message.reply(
            '😨 <i>У вас нет прав на выполнение этого действия</i>',
            reply_markup=markup
        )

    title = (
        message.text.split(" ", maxsplit=1)[1] if
        len(message.text.split(" ")) > 1 else ""
    ) if message.text else ""

    try:
        if not title_only:
            await bot.promote_chat_member(
                chat_id, other_id, False, True, False,
                can_delete_messages=True, can_manage_voice_chats=True,
                can_pin_messages=True, can_restrict_members=True,
                can_invite_users=True, can_promote_members=False)
        else:
            await bot.promote_chat_member(
                chat_id, other_id, False, True)
        await bot.set_chat_administrator_custom_title(
            chat_id, other_id, custom_title=title if title else
            "Модератор чата"
        )

        await message.reply_to_message.reply(
            '😎 <i>Вы стали администратором чата, круто!</i>'
        )
    except Exception:
        return await message.reply(
            '😨 <i>Произошла ошибка. Возможно, у Живополиса недостаточно'
            ' прав</i>',
            reply_markup=markup
        )


async def pin_message(message: Message) -> None:
    '''
    Pin chat message.

    :param message - moderator's message:
    '''
    user_id = message.from_user.id
    markup = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(
                    text="🥱 Понятно",
                    callback_data="cancel_action"
                )
            )
    chat_id = message.chat.id

    member = await bot.get_chat_member(chat_id, user_id)
    if not (member.is_chat_admin() or member.is_chat_owner()) \
       or not member['can_pin_messages']:
        return await message.reply(
            '😨 <i>У вас нет прав на выполнение этого действия</i>',
            reply_markup=markup
        )

    try:
        await bot.pin_chat_message(chat_id,
                                   message.reply_to_message.message_id)
        await message.reply_to_message.reply(
            '<i>😊 Сообщение закреплено</i>'
        )
    except Exception:
        return await message.reply(
            '😨 <i>Произошла ошибка. Возможно, у Живополиса недостаточно'
            ' прав</i>',
            reply_markup=markup
        )


async def unpin_message(message: Message) -> None:
    '''
    Unpin chat message.

    :param message - moderator's message:
    '''
    user_id = message.from_user.id
    markup = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(
                    text="🥱 Понятно",
                    callback_data="cancel_action"
                )
            )
    chat_id = message.chat.id

    member = await bot.get_chat_member(chat_id, user_id)
    if not (member.is_chat_admin() or member.is_chat_owner()) \
       or not member['can_pin_messages']:
        return await message.reply(
            '😨 <i>У вас нет прав на выполнение этого действия</i>',
            reply_markup=markup
        )

    try:
        await bot.unpin_chat_message(chat_id,
                                     message.reply_to_message.message_id)
        await message.reply_to_message.reply(
            '<i>🤔 Сообщение откреплено</i>'
        )
    except Exception:
        return await message.reply(
            '😨 <i>Произошла ошибка. Возможно, у Живополиса недостаточно'
            ' прав</i>',
            reply_markup=markup
        )


async def moderate(message: Message) -> None:
    '''
    Moderate the chat (only available for chat owner).

    :param message - moderator's message:
    '''
    user_id = message.from_user.id
    markup = InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(
                    text="🥱 Понятно",
                    callback_data="cancel_action"
                )
            )
    chat_id = message.chat.id
    text = message.text.split(" ", maxsplit=2)
    if re.fullmatch(r'!moderate<[-,0-9]+>', text[0]):
        id = text[0].replace("!moderate<", "")[:-1]
        try:
            chat = await bot.get_chat(int(id))
            chat_id = chat.id
        except Exception:
            return await message.reply(
                '😨 <i>Такого чата не существует</i>',
                reply_markup=markup
            )

    member = await bot.get_chat_member(chat_id, user_id)
    if not member.is_chat_owner() and message.text != '!moderate chat_id':
        return await message.reply(
            '😨 <i>Пользоваться этой командой может только владелец чата</i>',
            reply_markup=markup
        )

    if len(text) < 2:
        return await message.reply(
            '😨 <i>Данная команда должна иметь минимум 1 аргумент</i>',
            reply_markup=markup
        )

    command = text[1]
    flags = text[2].split(", ") if len(text) > 2 else []
    require_reply = ["ban_forever", "ban", "unban", "kick", "ban_channel",
                     "unban_channel"]

    if not message.reply_to_message and command in require_reply:
        return await message.reply(
            '😨 <i>Ответьте на нужное сообщение</i>',
            reply_markup=markup
        )

    if command == "ban":
        time = decode_term(flags[0]) if len(flags) > 0 else ""
        if not isinstance(time, int):
            return await message.reply(
                '😨 <i>Предоставлен неверный срок бана</i>',
                reply_markup=markup
            )

    try:
        match(command):
            case "ban_forever":
                await bot.ban_chat_member(
                    chat_id, message.reply_to_message.from_user.id,
                    revoke_messages=flags.__contains__("r")
                )
            case "ban":
                await bot.ban_chat_member(
                    chat_id, message.reply_to_message.from_user.id,
                    revoke_messages=flags.__contains__("r"),
                    until_date=current_time()+time
                )
            case "unban":
                await bot.unban_chat_member(
                    chat_id, message.reply_to_message.from_user.id,
                    only_if_banned=True
                )
            case "kick":
                await bot.unban_chat_member(
                    chat_id, message.reply_to_message.from_user.id
                )
            case "ban_channel":
                await bot.ban_chat_sender_chat(
                    chat_id, message.reply_to_message.sender_chat.id
                    if message.reply_to_message.sender_chat else
                    message.reply_to_message.from_user.id
                )
            case "unban_channel":
                await bot.unban_chat_sender_chat(
                    chat_id, message.reply_to_message.sender_chat.id
                    if message.reply_to_message.sender_chat else
                    message.reply_to_message.from_user.id
                )
            case "unpin":
                await bot.unpin_all_chat_messages(chat_id)
            case "mute":
                await bot.set_chat_permissions(
                    chat_id, ChatPermissions(False)
                )
            case "unmute":
                permissions = (
                    ChatPermissions(True) if 't' in flags else
                    ChatPermissions(
                        *[True for i in range(8)]
                    )
                )
                await bot.set_chat_permissions(
                    chat_id, permissions
                )
            case "chat_id":
                return await message.reply(
                    '<i><b>🆔 Данные чата:</b>\n\nID: <code>'
                    f'{message.chat.id}</code>.\nЗаголовок: <code>'
                    f'{message.chat.title}</code>.\nУчастников: <b>'
                    f'{await bot.get_chat_member_count(message.chat.id)}'
                    '</b></i>'
                )
            case _:
                return await message.reply(
                    '😨 <i>Неизвестная команда</i>',
                    reply_markup=markup
                )
        reply_message = (
            message.reply_to_message if message.reply_to_message else message
        )
        await reply_message.reply(
            '<i>🤔 Действие выполнено</i>'
        )
    except Exception as e:
        return await message.reply(
            '😨 <i>Произошла ошибка. Возможно, у Живополиса недостаточно'
            f' прав.\n\n<b>Текст ошибки:</b> <code>{e}</code></i>',
            reply_markup=markup
        )
