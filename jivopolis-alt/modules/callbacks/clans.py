import contextlib
from ... import bot, tglog

from ...misc import get_embedded_link
from ...database import cur, insert_clan
from ..start import StartCommand

from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from aiogram.utils.exceptions import BadRequest


async def create_clan(call: CallbackQuery) -> None:
    '''
    Callback for clan creating.

    :param call - callback:
    '''
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    member = await bot.get_chat_member(chat_id, user_id)

    if (
        not member.is_chat_admin()
        and not member.is_chat_creator()
    ):
        return await call.answer(
            '👀 Создать клан может только администратор чата',
            show_alert=True
        )

    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()

    if count >= 1:
        return await call.answer(
            '🚥 Такой клан уже существует. Для создания нового сначала'
            ' распустите старый',
            show_alert=True
        )
    try:
        link = await insert_clan(call.message.chat, call.from_user)
    except BadRequest as e:
        if str(e) == 'Not enough rights to manage chat invite link':
            return await call.message.edit_text(
                f"<i>{call.message.text}\n\n>>>🚨 Пожалуйста, сначала дайте "
                "боту права администратора</i>"
            )
        else:
            raise

    await tglog(
            message=(
                f"<b>🏘 {await get_embedded_link(user_id)}</b>"
                f" создал новый клан: <b><a href='{link}'>"
                f"{call.message.chat.title}</a></b>. <code>[{chat_id}]</code>"
            ),
            tag='#new_clan'
    )
    await bot.send_message(
        chat_id,
        text=(
            f"<i>🏘 <b>{await get_embedded_link(user_id)}</b> создал новый клан"
            ". Скорее присоединяйтесь!</i>"
        ),
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton('➕ Присоединиться', callback_data='join_clan')
        )
    )

    await StartCommand()._clan_start(call.message.chat)


async def joinclan(call: CallbackQuery, user_id: int) -> None:
    '''
    Callback for clan joining

    :param call - callback:
    :param user_id:
    '''
    chat_id = call.message.chat.id

    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()

    if count < 1:
        return await call.answer(
            "😓 Похоже, такого клана не существует",
            show_alert=True
        )
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    user_clan = cur.select("clan_id", "userdata").where(user_id=user_id).one()

    if not user_clan or user_clan != chat_id:
        cur.update("userdata").set(clan_id=chat_id).where(
            user_id=user_id).commit()
        await bot.send_message(
            chat_id,
            f'<i><b>{await get_embedded_link(user_id)}</b> присоединился к '
            'клану</i>'
        )

        if user_clan:
            with contextlib.suppress(Exception):
                await bot.send_message(
                    user_clan,
                    f"<i><b>{await get_embedded_link(user_id)}</b> вышел из"
                    " клана</i>"
                )
    else:
        cur.update("userdata").set(
            clan_id=None).where(user_id=user_id).commit()
        await bot.send_message(
            chat_id,
            f"<i><b>{await get_embedded_link(user_id)}</b> вышел из клана</i>"
        )


async def leaveclan(call: CallbackQuery) -> None:
    """
    Callback for leave clan

    :param call - callback:
    """
    user_id = call.from_user.id
    user_clan = cur.select("clan_id", "userdata").where(user_id=user_id).one()

    if not user_clan or user_clan != call.message.chat.id:
        return await call.answer(
            "🤥 Но ты ведь не состоишь в этом клане… Нельзя выйти, если ты не "
            "заходил, дорогой!",
            show_alert=True
        )

    cur.update("userdata").set(clan_id=None).where(
        user_id=user_id).commit()

    await call.message.answer(
        f"<i><b>{await get_embedded_link(user_id)}</b> вышел из клана</i>")


async def clan_members(call: CallbackQuery) -> None:
    """
    Callback for clan members list

    :param call - callback:
    """
    clan_id = call.message.chat.id
    count = cur.select("count(*)", "clandata").where(clan_id=clan_id).one()

    if count < 1:
        return await call.answer(
            "😓 Похоже, такого клана не существует",
            show_alert=True
        )
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    text = ''
    clan_owner = cur.select("owner_id", "clandata").where(
        clan_id=clan_id).one()
    clan_members = cur.select("user_id", "userdata").where(
        clan_id=clan_id).fetch()

    if clan_owner:
        text += (
            f'👑 Создатель клана:\n{await get_embedded_link(clan_owner)}\n\n'
        )
    if len(clan_members) > 0:
        text += '👥 Участники клана:'
        for member_id in clan_members:
            text += f'\n{await get_embedded_link(member_id[0])}'

    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text='◀ Скрыть',
            callback_data='cancel_action'
        )
    )
    await call.message.answer(f'<i><b>{text}</b></i>', reply_markup=markup)


async def call_clan(call: CallbackQuery):
    """
    Callback to call all clan members

    :param call - callback:
    """
    chat_id = call.message.chat.id
    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()

    if count < 1:
        return await call.answer(
            "😓 Похоже, такого клана не существует",
            show_alert=True
        )
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    member = await bot.get_chat_member(chat_id, call.from_user.id)
    if (
        not member.is_chat_admin()
        and not member.is_chat_creator()
    ):
        return await call.answer(
            '👀 Созывать клан может только администратор чата',
            show_alert=True
        )

    clan_members = cur.select("user_id", "userdata").where(
        clan_id=chat_id).fetch()
    clan_name = cur.select("clan_name", "clandata").where(
        clan_id=chat_id).one()
    link = cur.select("link", "clandata").where(
        clan_id=chat_id).one()

    sent_successfully = 0
    errors = 0
    user_not_exists = 0
    blocked_bot = 0
    for member_id in clan_members:
        try:
            await bot.send_message(
                chat_id=member_id[0],
                text=f'<i>📣 Вас созывает клан <b><a href="{link}">'
                     f'{clan_name}</a></b></i>'
            )
            sent_successfully += 1
        except Exception as e:
            match (str(e)):
                case (
                    "Chat not found" |
                    "Forbidden: user is deactivated" |
                    "Forbidden: bot can't send messages to bots"
                ):
                    user_not_exists += 1
                case 'Forbidden: bot was blocked by the user':
                    blocked_bot += 1
                case _:
                    errors += 1

    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text='✔ Готово',
            callback_data='cancel_action'
        )
    )

    await call.message.answer(
        '<i><b>📣 Созыв участников завершён</b>\n\n'
        f'✅ Успешно созвано: <b>{sent_successfully}</b>\n'
        '🚮 Пользователи не существуют или удалены из Telegram: '
        f'<b>{user_not_exists}</b>\n✋ Заблокировали Живополис: '
        f'<b>{blocked_bot}</b>\n❌ Другие ошибки: <b>{errors}</b></i>',
        reply_markup=markup
    )


async def clan_top(call: CallbackQuery):
    """
    Callback for 10 clans with the greatest balance

    :param call - callback:
    """

    clans = cur.execute(
        "SELECT * FROM clandata WHERE clan_type=\"public\" AND "
        "clan_balance<1000000 ORDER BY -clan_balance LIMIT 20"
    )

    clan_text = ''
    clan_number = 1
    for clan in clans:
        clan_text += (
            f'{clan_number}. \n<a href="{clan[8]}">{clan[2]}</a> - ${clan[4]}'
            '\n'
        )
        clan_number += 1

    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text='◀ Скрыть',
            callback_data='cancel_action'
        )
    )

    await call.message.answer(
        f'<i><b>🏆 Топ кланов по балансу\n\n{clan_text}</b></i>',
        reply_markup=markup
    )


async def clan_settings(call: CallbackQuery):
    """
    Callback for clan settings

    :param call - callback:
    """
    chat_id = call.message.chat.id
    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()

    if count < 1:
        return await call.answer(
            "😓 Похоже, такого клана не существует",
            show_alert=True
        )
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    member = await bot.get_chat_member(chat_id, call.from_user.id)
    if (
        not member.is_chat_admin()
        and not member.is_chat_creator()
    ):
        return await call.answer(
            '👀 Управлять кланом может только администратор чата',
            show_alert=True
        )

    clan_type = cur.select("clan_type", "clandata").where(
        clan_id=chat_id).one()
    clan_type_ru = 'Частный' if clan_type == 'private' else 'Публичный'
    clan_hq = cur.select("HQ_place", "clandata").where(
        clan_id=chat_id).one()
    user_place = cur.select("current_place", "userdata").where(
        user_id=call.from_user.id).one()

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text=f'🔐 Тип клана: {clan_type_ru}',
            callback_data='toggle_clan_type'
        ),
        InlineKeyboardButton(
            text='✏ Профиль клана',
            callback_data='clan_profile'
        ),
        InlineKeyboardButton(
            text=f'🏬 Построить ШК: {user_place}',
            callback_data='clan_hq'
        ) if clan_hq == 'не установлено' else InlineKeyboardButton(
            text='🏬❌ Снести штаб-квартиру',
            callback_data='clan_hq'
        ),
        InlineKeyboardButton(
            text='🗑 Распустить клан',
            callback_data='delete_clan'
        ),
        InlineKeyboardButton(
            text='◀ Назад',
            callback_data='cancel_action'
        )
    )

    await call.message.answer(
        '<i>⚙ Настройки клана</i>',
        reply_markup=markup
    )


async def clan_profile(call: CallbackQuery):
    """
    Callback for clan profile settings

    :param call - callback:
    """
    chat_id = call.message.chat.id
    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()

    if count < 1:
        return await call.answer(
            "😓 Похоже, такого клана не существует",
            show_alert=True
        )
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    member = await bot.get_chat_member(chat_id, call.from_user.id)
    if (
        not member.is_chat_admin()
        and not member.is_chat_creator()
    ):
        return await call.answer(
            '👀 Управлять кланом может только администратор чата',
            show_alert=True
        )

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='✏ Изменить название клана',
            callback_data='set_clan_name'
        ),
        InlineKeyboardButton(
            text='📝 Изменить описание клана',
            callback_data='set_clan_bio'
        ),
        InlineKeyboardButton(
            text='📎 Изменить ссылку на клан',
            callback_data='set_clan_link'
        ),
        InlineKeyboardButton(
            text='◀ Назад',
            callback_data='cancel_action'
        )
    )

    await call.message.answer(
        '<i>✏ Настройки профиля клана</i>',
        reply_markup=markup
    )


async def delete_clan(call: CallbackQuery):
    """
    Callback for a clan deleting menu

    :param call - callback:
    """
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()

    if count < 1:
        return await call.answer(
            "😓 Похоже, такого клана не существует",
            show_alert=True
        )
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    owner = cur.select("owner_id", "clandata").where(clan_id=chat_id).one()
    if owner != user_id:
        return await call.answer(
            '👀 Распустить клан может только его создатель',
            show_alert=True
        )

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='✅ Подтвердить',
            callback_data='delete_clan_confirm'
        ),
        InlineKeyboardButton(
            text='❌ Отмена',
            callback_data='cancel_action'
        )
    )

    await call.message.answer(
        '<i>😨 Вы точно хотите удалить ваш клан вместе со всеми его '
        'деньгами, дополнениями и постройками? Это действие невозможно '
        'отменить</i>',
        reply_markup=markup
    )


async def delete_clan_confirm(call: CallbackQuery):
    """
    Callback for clan removal

    :param call - callback:
    """
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()

    if count < 1:
        return await call.answer(
            "😓 Похоже, такого клана не существует",
            show_alert=True
        )
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    owner = cur.select("owner_id", "clandata").where(clan_id=chat_id).one()
    if owner != user_id:
        return await call.answer(
            '👀 Распустить клан может только его создатель',
            show_alert=True
        )

    name = cur.select("clan_name", "clandata").where(clan_id=chat_id).one()
    cur.execute(
        "DELETE FROM clandata WHERE clan_id=?", (chat_id,)
    ).commit()

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='😪 Хорошо',
            callback_data='cancel_action'
        ),
        InlineKeyboardButton(
            text='➕ Создать новый клан',
            callback_data='create_clan'
        )
    )
    await call.message.answer(
        '<i>😥 Вот и всё... Ваш клан канул в Лету. Вернуть его невозможно</i>',
        reply_markup=markup
    )

    await tglog(
            message=(
                f"😪 <b>{await get_embedded_link(user_id)}</b>"
                f" распустил клан <b>{name}</b>. <code>[{chat_id}]</code>"
            ),
            tag='#delete_clan'
    )


async def toggle_clan_type(call: CallbackQuery):
    """
    Callback for a clan type changing setting

    :param call - callback:
    """
    chat_id = call.message.chat.id
    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()

    if count < 1:
        return await call.answer(
            "😓 Похоже, такого клана не существует",
            show_alert=True
        )
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    member = await bot.get_chat_member(chat_id, call.from_user.id)
    if (
        not member.is_chat_admin()
        and not member.is_chat_creator()
    ):
        return await call.answer(
            '👀 Управлять кланом может только администратор чата',
            show_alert=True
        )

    clan_type = cur.select("clan_type", "clandata").where(
        clan_id=chat_id).one()
    new_clan_type = 'public' if clan_type == 'private' else 'private'
    new_clan_type_ru = 'Публичный' if new_clan_type == 'public' else 'Частный'

    if call.message.chat.username is None:
        chat_data = await bot.get_chat(chat_id)
        username = chat_data.invite_link
    else:
        username = f't.me/{call.message.chat.username}'
    if not username:
        return await call.answer(
            '🚨 Пожалуйста, сначала дайте боту права администратора',
            show_alert=True
        )

    cur.update("clandata").set(clan_type=new_clan_type).where(
        clan_id=chat_id).commit()
    cur.update("clandata").set(link=username).where(clan_id=chat_id).commit()

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='✅ Готово',
            callback_data='cancel_action'
        )
    )
    await call.message.answer(
        f'<i>🥳 Тип вашего клана изменён на <b>{new_clan_type_ru}</b></i>',
        reply_markup=markup
    )


async def clan_hq(call: CallbackQuery):
    """
    Callback for building or demolition of clan headquarters

    :param call - callback:
    """
    chat_id = call.message.chat.id
    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()

    if count < 1:
        return await call.answer(
            "😓 Похоже, такого клана не существует",
            show_alert=True
        )
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    member = await bot.get_chat_member(chat_id, call.from_user.id)
    if (
        not member.is_chat_admin()
        and not member.is_chat_creator()
    ):
        return await call.answer(
            '👀 Управлять кланом может только администратор чата',
            show_alert=True
        )

    clan_hq = cur.select("HQ_place", "clandata").where(
        clan_id=chat_id).one()
    user_place = cur.select("current_place", "userdata").where(
        user_id=call.from_user.id).one()

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='✅ Готово',
            callback_data='cancel_action'
        )
    )

    if clan_hq == 'не установлено':
        address = cur.select("MAX(address)+1", "clandata").where(
            HQ_place=user_place).one()
        address = address or 1
        cur.update("clandata").set(HQ_place=user_place).where(
            clan_id=chat_id).commit()
        cur.update("clandata").set(address=address).where(
            clan_id=chat_id).commit()
        await call.message.answer(
            f'<i>🥳 Штаб-квартира построена по адресу <b>{user_place}, '
            f'{address}</b></i>',
            reply_markup=markup
        )
    else:
        cur.update("clandata").set(HQ_place='не установлено').where(
            clan_id=chat_id).commit()
        cur.update("clandata").set(address=0).where(
            clan_id=chat_id).commit()
        await call.message.answer(
            '<i>😪 Штаб-квартира вашего клана снесена</i>',
            reply_markup=markup
        )


async def set_clan_name(call: CallbackQuery) -> None:
    '''
    Callback for clan name setting

    :param call - callback*
    '''
    chat_id = call.message.chat.id
    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()

    if count < 1:
        return await call.answer(
            "😓 Похоже, такого клана не существует",
            show_alert=True
        )
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    member = await bot.get_chat_member(chat_id, call.from_user.id)
    if (
        not member.is_chat_admin()
        and not member.is_chat_creator()
    ):
        return await call.answer(
            '👀 Управлять кланом может только администратор чата',
            show_alert=True
        )

    cur.update("userdata").set(process="set_clan_name").where(
        user_id=call.from_user.id).commit()

    await call.message.answer(
        "<i>✏ Введите новое название клана</i>",
        reply_markup=InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(
                text="🔄 По умолчанию",
                callback_data="delete_clan_name"
            ),
            InlineKeyboardButton(
                text="🚫 Отмена",
                callback_data="cancel_process"
            )
        )
    )


async def delete_clan_name(call: CallbackQuery) -> None:
    '''
    Callback for clan name resetting

    :param call - callback:
    '''
    chat_id = call.message.chat.id
    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()

    if count < 1:
        return await call.answer(
            "😓 Похоже, такого клана не существует",
            show_alert=True
        )
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    member = await bot.get_chat_member(chat_id, call.from_user.id)
    if (
        not member.is_chat_admin()
        and not member.is_chat_creator()
    ):
        return await call.answer(
            '👀 Управлять кланом может только администратор чата',
            show_alert=True
        )

    cur.update("userdata").set(process="").where(
        user_id=call.from_user.id).commit()
    cur.update("clandata").set(clan_name=call.message.chat.title).where(
        clan_id=chat_id).commit()

    await call.message.answer(
        "<i>👌 Название клана успешно изменено</i>",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="✅ Готово",
                callback_data="cancel_action"
            )
        )
    )


async def set_clan_link(call: CallbackQuery) -> None:
    '''
    Callback for clan link setting

    :param call - callback:
    '''
    chat_id = call.message.chat.id
    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()

    if count < 1:
        return await call.answer(
            "😓 Похоже, такого клана не существует",
            show_alert=True
        )
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    member = await bot.get_chat_member(chat_id, call.from_user.id)
    if (
        not member.is_chat_admin()
        and not member.is_chat_creator()
    ):
        return await call.answer(
            '👀 Управлять кланом может только администратор чата',
            show_alert=True
        )

    cur.update("userdata").set(process="set_clan_link").where(
        user_id=call.from_user.id).commit()

    await call.message.answer(
        "<i>📎 Введите новую ссылку на клан.\n\n<b>‼ Внимание! </b>"
        "Ссылка на клан может вести только на некоммерческий "
        "Telegram-чат, бот или канал, связанный с Живополисом, "
        "либо на пользователя Telegram при его согласии (если "
        "пользователь имеет прямое отношение к клану).\n\n"
        "Если ссылка вашего клана будет вести на коммерческий "
        "ресурс, внешний ресурс или ресурс, не имеющий прямого "
        "отношения к Живополису, мы можем заблокировать вас или ваш "
        "клан. Мы вас предупредили</i>",
        reply_markup=InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(
                text="🔄 По умолчанию",
                callback_data="delete_clan_link"
            ),
            InlineKeyboardButton(
                text="🚫 Отмена",
                callback_data="cancel_process"
            )
        )
    )


async def delete_clan_link(call: CallbackQuery) -> None:
    '''
    Callback for custom clan link resetting

    :param call - callback:
    '''
    chat_id = call.message.chat.id
    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()

    if count < 1:
        return await call.answer(
            "😓 Похоже, такого клана не существует",
            show_alert=True
        )
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    member = await bot.get_chat_member(chat_id, call.from_user.id)
    if (
        not member.is_chat_admin()
        and not member.is_chat_creator()
    ):
        return await call.answer(
            '👀 Управлять кланом может только администратор чата',
            show_alert=True
        )

    cur.update("userdata").set(process="").where(
        user_id=call.from_user.id).commit()

    if call.message.chat.username is None:
        getchat = await bot.get_chat(chat_id)
        new_chat_link = getchat.invite_link
        if not new_chat_link:
            return await call.answer(
                "🚨 Пожалуйста, сначала дайте боту права "
                "администратора",
                show_alert=True
            )
    else:
        new_chat_link = f't.me/{call.message.chat.username}'
    cur.update("clandata").set(link=new_chat_link).where(
        clan_id=chat_id).commit()

    await call.message.answer(
        "<i>👌 Ссылка на клан успешно изменена</i>",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="✅ Готово",
                callback_data="cancel_action"
            )
        )
    )


async def set_clan_bio(call: CallbackQuery) -> None:
    '''
    Callback for clan bio setting

    :param call - callback:
    '''
    chat_id = call.message.chat.id
    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()

    if count < 1:
        return await call.answer(
            "😓 Похоже, такого клана не существует",
            show_alert=True
        )
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    member = await bot.get_chat_member(chat_id, call.from_user.id)
    if (
        not member.is_chat_admin()
        and not member.is_chat_creator()
    ):
        return await call.answer(
            '👀 Управлять кланом может только администратор чата',
            show_alert=True
        )

    cur.update("userdata").set(process="set_clan_bio").where(
        user_id=call.from_user.id).commit()

    await call.message.answer(
        "<i>📝 Введите новое описание клана</i>",
        reply_markup=InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(
                text="🗑 Удалить описание клана",
                callback_data="delete_clan_bio"
            ),
            InlineKeyboardButton(
                text="🚫 Отмена",
                callback_data="cancel_process"
            )
        )
    )


async def delete_clan_bio(call: CallbackQuery) -> None:
    '''
    Callback for clan bio deleting

    :param call - callback:
    '''
    chat_id = call.message.chat.id
    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()

    if count < 1:
        return await call.answer(
            "😓 Похоже, такого клана не существует",
            show_alert=True
        )
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    member = await bot.get_chat_member(chat_id, call.from_user.id)
    if (
        not member.is_chat_admin()
        and not member.is_chat_creator()
    ):
        return await call.answer(
            '👀 Управлять кланом может только администратор чата',
            show_alert=True
        )

    cur.update("userdata").set(process="").where(
        user_id=call.from_user.id).commit()
    cur.update("clandata").set(description="").where(
        clan_id=chat_id).commit()

    await call.message.answer(
        "<i>👌 Описание клана успешно удалено</i>",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="✅ Готово",
                callback_data="cancel_action"
            )
        )
    )


async def confirm_clan_profile_setting(message: Message, setting: str) -> None:
    '''
    Callback for changing a clan profile setting

    :param message - message:
    :param setting - the setting to be changed:
    '''
    chat_id = message.chat.id
    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()

    failure_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text='😪 Хорошо',
            callback_data='cancel_action'
        )
    )

    if count < 1:
        return await message.reply(
            "<i>😓 Похоже, такого клана не существует</i>",
            reply_markup=failure_markup
        )
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    member = await bot.get_chat_member(chat_id, message.from_user.id)
    if (
        not member.is_chat_admin()
        and not member.is_chat_creator()
    ):
        return await message.reply(
            '<i>👀 Управлять кланом может только администратор чата</i>',
            reply_markup=failure_markup
        )

    cur.update("clandata").set(**{setting: message.text}).where(
        clan_id=chat_id).commit()

    await message.answer(
        "<i>🥳 Данные клана успешно изменены</i>",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="✅ Готово",
                callback_data="cancel_action"
            )
        )
    )
