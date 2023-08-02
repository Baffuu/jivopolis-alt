from .. import bot
from ..database.functions import current_time
from aiogram.types import (
    Message, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
)


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
        except ValueError:
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
        term_identifier = message.text.replace(" ", "").replace("/mute", "")
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
