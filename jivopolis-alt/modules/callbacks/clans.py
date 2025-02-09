import contextlib
from ... import bot, tglog
import asyncio
import random

from ...misc import get_embedded_link, get_time_units
from ...misc.config import addon_prices, addon_descriptions, filter_names
from ...misc.constants import MINIMUM_PUBLIC_CLAN_LEVEL
from ...database import cur, insert_clan
from ...database.functions import (
    buybutton, current_time, prison_sentence, weather_damage
)
from ..start import StartCommand
from ...clanbuildings import CLAN_BUILDINGS

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

    clan_text = ''.join(
        f'{clan_number}. \n<a href="{clan[8]}">{clan[2]}</a> - ${clan[4]}\n'
        for clan_number, clan in enumerate(clans, start=1)
    )
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
        )
    )
    if clan_hq != 'не установлено':
        markup.add(
            InlineKeyboardButton(
                text='🏛 Клан-локация',
                callback_data='addon_location'
            )
        )
    markup.add(
        InlineKeyboardButton(
            text='🛠 Функционал клана',
            callback_data='clan_features'
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
            text='🖼 Изменить аватарку клана',
            callback_data='set_clan_photo'
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

    if new_clan_type == 'public':
        owner = cur.select("owner_id", "clandata").where(clan_id=chat_id).one()
        level = cur.select("level", "userdata").where(
            user_id=owner).one()

        if level < MINIMUM_PUBLIC_CLAN_LEVEL:
            return await call.answer(
                '🚫 Уровень владельца клана должен быть не меньше '
                f'{MINIMUM_PUBLIC_CLAN_LEVEL}, чтобы клан стал публичным',
                show_alert=True
            )

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

    await weather_damage(call.from_user.id,
                         call.message.chat.id)


async def set_clan_name(call: CallbackQuery) -> None:
    '''
    Callback for clan name setting

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


async def set_clan_photo(call: CallbackQuery) -> None:
    '''
    Callback for clan profile picture setting

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

    cur.update("userdata").set(process="set_clan_photo").where(
        user_id=call.from_user.id).commit()

    await call.message.answer(
        "<i>📝 Отправьте новое фото клана (в сжатом виде) "
        "или ссылку на фото</i>",
        reply_markup=InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(
                text="🗑 Удалить аватарку клана",
                callback_data="delete_clan_photo"
            ),
            InlineKeyboardButton(
                text="🚫 Отмена",
                callback_data="cancel_process"
            )
        )
    )


async def delete_clan_photo(call: CallbackQuery) -> None:
    '''
    Callback for clan profile picture deleting

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
    cur.update("clandata").set(photo_id="").where(
        clan_id=chat_id).commit()

    await call.message.answer(
        "<i>👌 Аватарка клана успешно удалена</i>",
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


async def confirm_clan_photo(message: Message) -> None:
    '''
    Callback for changing clan profile picture

    :param message - message:
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

    if len(message.photo) == 0:
        new_photo = message.text
    else:
        new_photo = message.photo[0].file_id

    try:
        await message.answer_photo(
            new_photo,
            "<i>🥳 Фото клана успешно изменено</i>",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(
                    text="✅ Готово",
                    callback_data="cancel_action"
                )
            )
        )
        cur.update("clandata").set(photo_id=new_photo).where(
            clan_id=chat_id).commit()
    except Exception:
        await message.answer(
            '😨 <i>Видимо, вы отправили не фото и не ссылку на фото</i>',
            reply_markup=failure_markup.add(
                InlineKeyboardButton(
                    text='🔄 Заново',
                    callback_data='set_clan_photo'
                )
            )
        )


async def buy_clan_addon(call: CallbackQuery, addon: str) -> None:
    '''
    Callback for buying a clan addon

    :param call - callback:
    :param addon - addon symbolic name:
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

    if (
        cur.select(f"addon_{addon}", "clandata")
        .where(clan_id=chat_id)
        .one()
    ):
        return await call.answer(
            '🤨 В клане уже есть это дополнение, зачем вам ещё одно?',
            show_alert=True
        )

    balance = cur.select("balance", "userdata").where(
        user_id=call.from_user.id).one()
    if balance < addon_prices[addon]:
        return await call.answer(
            '😪 У вас недостаточно денег',
            show_alert=True
        )

    cur.update("userdata").add(balance=-addon_prices[addon]).where(
        user_id=call.from_user.id).commit()
    cur.update("clandata").set(**{f'addon_{addon}': 1}).where(
        clan_id=chat_id).commit()

    await call.message.answer(
        "<i>👌 Дополнение успешно добавлено</i>",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="✅ Готово",
                callback_data="cancel_action"
            )
        )
    )


async def sell_clan_addon(call: CallbackQuery, addon: str) -> None:
    '''
    Callback for unbuying a clan addon

    :param call - callback:
    :param addon - addon symbolic name:
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

    addon_amount = cur.select(f"addon_{addon}", "clandata").where(
        clan_id=chat_id).one()
    if not addon_amount:
        return await call.answer(
            '🤨 В клане нет этого дополнения, что вы собрались продавать?',
            show_alert=True
        )

    cur.update("userdata").add(balance=addon_prices[addon]).where(
        user_id=call.from_user.id).commit()
    cur.update("clandata").set(**{f'addon_{addon}': 0}).where(
        clan_id=chat_id).commit()

    await call.message.answer(
        "<i>👌 Дополнение успешно продано</i>",
        reply_markup=InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(
                text="✅ Готово",
                callback_data="cancel_action"
            )
        )
    )


async def clan_addon_menu(call: CallbackQuery, addon: str):
    '''
    Callback for a clan addon menu

    :param call - callback:
    :param addon - addon symbolic name:
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

    addon_amount = cur.select(f"addon_{addon}", "clandata").where(
        clan_id=chat_id).one()

    cost = addon_prices[addon]
    description = addon_descriptions[addon]

    markup = InlineKeyboardMarkup(row_width=1)
    if addon == "gameclub" and addon_amount:
        timeout = cur.select("game_timeout", "clandata").where(
            clan_id=chat_id).one()
        markup.add(
            InlineKeyboardButton(
                text=f"⏱ Кулдаун: {timeout} с",
                callback_data="set_gameclub_timeout"
            )
        )

    await call.message.answer(
        f"<i>{description}.\n\n💸 Включение дополнения стоит <b>${cost}"
        "</b>. При отмене покупки эта сумма возвращается тому администратору,"
        " кто её отменил</i>",
        reply_markup=markup.add(
            InlineKeyboardButton(
                text="❌ Отменить покупку",
                callback_data=f"selladdon_{addon}"
            ) if addon_amount else InlineKeyboardButton(
                            text=f"✅ Купить (${cost})",
                            callback_data=f"buyaddon_{addon}"
                        ),
            InlineKeyboardButton(
                text="◀ Назад",
                callback_data="cancel_action"
            )
        )
    )


async def clan_features(call: CallbackQuery):
    """
    Callback for clan features menu

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
            text='📛 Фильтр сообщений',
            callback_data='clan_filter'
        ),
        InlineKeyboardButton(
            text='🎰 Мини-казино',
            callback_data='addon_gameclub'
        ),
        InlineKeyboardButton(
            text='◀ Назад',
            callback_data='cancel_action'
        )
    )

    await call.message.answer(
        '<i>🛠 Функционал клана</i>',
        reply_markup=markup
    )


async def set_gameclub_timeout(call: CallbackQuery):
    """
    Callback for game club timeout menu

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

    amount = cur.select("addon_gameclub", "clandata").where(
        clan_id=chat_id).one()
    if not amount:
        return await call.answer(
            '🤔 Сначала приобретите дополнение "Мини-казино"',
            show_alert=True
        )

    timeout = cur.select("game_timeout", "clandata").where(
        clan_id=chat_id).one()
    markup = InlineKeyboardMarkup(row_width=5)
    optionlist = [
        InlineKeyboardButton(
            text=f"{option} с", callback_data=f"set_timeout_{option}"
        )
        for option in ["5", "10", "15", "20", "30", "45", "60", "90", "300"]
    ]
    markup.add(*optionlist)
    markup.add(
        InlineKeyboardButton(
            text="◀ Назад",
            callback_data="cancel_action"
        )
    )

    await call.message.answer(
        '<i>⏱ Выберите, какое минимальное время должно пройти между крутками'
        f' одного пользователя.\n\nТекущий кулдаун: <b>{timeout} с</b></i>',
        reply_markup=markup
    )


async def confirm_timeout(call: CallbackQuery, timeout: int):
    """
    Callback for game club timeout setting

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

    amount = cur.select("addon_gameclub", "clandata").where(
        clan_id=chat_id).one()
    if not amount:
        return await call.answer(
            '🤔 Сначала приобретите дополнение "Мини-казино"',
            show_alert=True
        )

    cur.update("clandata").set(game_timeout=timeout).where(
        clan_id=call.message.chat.id).commit()
    await clan_addon_menu(call, addon="gameclub")


async def clan_filter(call: CallbackQuery):
    """
    Callback for clan filter feature menu

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

    markup = InlineKeyboardMarkup(row_width=1)
    for filter in filter_names:
        filter_state = cur.select(f"filter_{filter}", "clandata").where(
            clan_id=chat_id).one()
        filter_state_ru = "Включено" if filter_state else "Выключено"
        markup.add(
            InlineKeyboardButton(
                f'{filter_names[filter]}: {filter_state_ru}',
                callback_data=f'toggle_filter_{filter}'
            )
        )

    markup.add(
        InlineKeyboardButton(
            text='◀ Назад',
            callback_data='cancel_action'
        )
    )

    await call.message.answer(
        '<i>📛 <b>Фильтр сообщений</b> удаляет сообщения определённого типа. '
        'Выберите, какие типы сообщений он будет удалять.\n\n<b>Обратите '
        'внимание!\n1.</b> Фильтр удаляет сообщения даже админов и создателя '
        'группы.\n<b>2.</b> Если у бота нет прав на удаление сообщений, он '
        'просто будет игнорировать все нарушения</i>',
        reply_markup=markup
    )


async def toggle_filter(call: CallbackQuery, filter: str):
    """
    Callback for toggling a filter

    :param call - callback:
    :param filter - filter name:
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

    filter_enabled = cur.select(f"filter_{filter}", "clandata").where(
        clan_id=chat_id).one()

    cur.update("clandata").set(**{f"filter_{filter}": abs(
        filter_enabled-1)}).where(clan_id=chat_id).commit()

    await call.message.delete()
    await clan_filter(call)


async def clan_buildings(call: CallbackQuery):
    """
    Callback for clan buildings menu

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

    markup = InlineKeyboardMarkup(row_width=1)
    for building in CLAN_BUILDINGS:
        amount = cur.select(f"build_{building}", "clandata").where(
            clan_id=chat_id).one()
        if amount > 0:
            build = CLAN_BUILDINGS[building]
            markup.add(
                InlineKeyboardButton(
                    text=build.ru_name,
                    callback_data=f'building_{building}'
                )
            )

    markup.add(
        InlineKeyboardButton(
            text='🏗 Магазин построек',
            callback_data='clan_building_shop'
        ),
        InlineKeyboardButton(
            text='◀ Назад',
            callback_data='cancel_action'
        )
    )

    await call.message.answer(
        '<i>🏙 Постройки клана</i>',
        reply_markup=markup
    )


async def clan_building_shop(call: CallbackQuery):
    """
    Callback for clan buildings shop

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

    markup = InlineKeyboardMarkup(row_width=1)
    for building in CLAN_BUILDINGS:
        build = CLAN_BUILDINGS[building]
        markup.add(
            InlineKeyboardButton(
                text=build.ru_name,
                callback_data=f'building_{building}'
            )
        )

    markup.add(
        InlineKeyboardButton(
            text='◀ Назад',
            callback_data='cancel_action'
        )
    )

    await call.message.answer(
        '<i>🏗 Магазин построек клана</i>',
        reply_markup=markup
    )


async def clan_building_menu(call: CallbackQuery, building: str):
    '''
    Callback for a clan building menu

    :param call - callback:
    :param addon - addon symbolic name:
    '''
    chat_id = call.message.chat.id
    build = CLAN_BUILDINGS[building]
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
        and CLAN_BUILDINGS[building].admins_only
    ):
        return await call.answer(
            '👀 Пользоваться данной постройкой может только администратор чата',
            show_alert=True
        )

    amount = cur.select(f"build_{building}", "clandata").where(
        clan_id=chat_id).one()

    cost = build.price
    description = build.description
    name = build.ru_name

    markup = InlineKeyboardMarkup(row_width=1)
    text = (
        f"<b>{name}</b> - {description}.\n\n💸 Покупка постройки стоит "
        f"<b>${cost}</b>. При отмене покупки эта сумма возвращается тому"
        " администратору, кто её отменил"
    )
    if build.max_level and amount:
        text += (
            f".\n\nЭту постройку можно улучшать вплоть до <b>{build.max_level}"
            "</b> уровня. Стоимость каждого апгрейда на <b>$"
            f"{build.upgrade_markup}</b> больше стоимости предыдущего.\n\n"
            "❗ При отмене покупки постройки возвращается её начальная"
            " стоимость без учёта улучшений.\n\nУровень постройки - "
            f"<b>{amount}</b>"
        )

    if amount:
        markup.add(
            InlineKeyboardButton(
                text="▶ Воспользоваться",
                callback_data=f"use_building_{building}"
            )
        )
        if build.max_level and amount <= build.max_level:
            cost = build.price + amount*build.upgrade_markup
            markup.add(
                InlineKeyboardButton(
                    text=f"↗ Улучшить (${cost})",
                    callback_data=f"upgrade_building_{building}"
                )
            )
        markup.add(
            InlineKeyboardButton(
                text="❌ Отменить покупку",
                callback_data=f"sellbuilding_{building}"
            )
        )
    else:
        markup.add(
            InlineKeyboardButton(
                text=f"🏗 Построить (${build.price})",
                callback_data=f"buybuilding_{building}"
            )
        )

    await call.message.answer(
        f"<i>{text}</i>",
        reply_markup=markup.add(
            InlineKeyboardButton(
                text="◀ Назад",
                callback_data="cancel_action"
            )
        )
    )


async def buy_clan_building(call: CallbackQuery, building: str) -> None:
    '''
    Callback for buying a clan building

    :param call - callback:
    :param building - building symbolic name:
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

    if (
        cur.select(f"build_{building}", "clandata")
        .where(clan_id=chat_id)
        .one()
    ):
        return await call.answer(
            '🤨 В клане уже есть эта постройка, зачем вам ещё одна?',
            show_alert=True
        )

    price = CLAN_BUILDINGS[building].price

    balance = cur.select("balance", "userdata").where(
        user_id=call.from_user.id).one()
    if balance < price:
        return await call.answer(
            '😪 У вас недостаточно денег',
            show_alert=True
        )

    cur.update("userdata").add(balance=-price).where(
        user_id=call.from_user.id).commit()
    cur.update("clandata").set(**{f'build_{building}': 1}).where(
        clan_id=chat_id).commit()

    await call.message.answer(
        "<i>👌 Постройка успешно куплена</i>",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="✅ Готово",
                callback_data="cancel_action"
            )
        )
    )


async def sell_clan_building(call: CallbackQuery, building: str) -> None:
    '''
    Callback for unbuying a clan building

    :param call - callback:
    :param building - building symbolic name:
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

    amount = cur.select(f"build_{building}", "clandata").where(
        clan_id=chat_id).one()
    if not amount:
        return await call.answer(
            '🤨 В клане уже нет этой постройки, что вы собрались продавать?',
            show_alert=True
        )

    price = CLAN_BUILDINGS[building].price

    cur.update("userdata").add(balance=price).where(
        user_id=call.from_user.id).commit()
    cur.update("clandata").set(**{f'build_{building}': 0}).where(
        clan_id=chat_id).commit()

    await call.message.answer(
        "<i>👌 Постройка успешно продана</i>",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="✅ Готово",
                callback_data="cancel_action"
            )
        )
    )


async def upgrade_clan_building(call: CallbackQuery, building: str) -> None:
    '''
    Callback for upgrading a clan building

    :param call - callback:
    :param building - building symbolic name:
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

    amount = cur.select(f"build_{building}", "clandata").where(
        clan_id=chat_id).one()
    if not amount:
        return await call.answer(
            '🤨 В клане нет этой постройки, что вы собрались улучшать?',
            show_alert=True
        )
    if amount >= CLAN_BUILDINGS[building].max_level:
        return await call.answer(
            '😪 Постройка уже улучшена до максимального уровня',
            show_alert=True
        )

    price = CLAN_BUILDINGS[building].price +\
        CLAN_BUILDINGS[building].upgrade_markup*amount

    balance = cur.select("balance", "userdata").where(
        user_id=call.from_user.id).one()
    if balance < price:
        return await call.answer(
            '😪 У вас недостаточно денег',
            show_alert=True
        )

    cur.update("userdata").add(balance=-price).where(
        user_id=call.from_user.id).commit()
    cur.update("clandata").add(**{f'build_{building}': 1}).where(
        clan_id=chat_id).commit()

    await call.message.answer(
        f"<i>👌 Постройка успешно улучшена до уровня <b>{amount+1}</b></i>",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="✅ Готово",
                callback_data="cancel_action"
            )
        )
    )


async def use_clan_building(call: CallbackQuery, building: str) -> None:
    '''
    Callback for using a clan building

    :param call - callback:
    :param building - building symbolic name:
    '''
    chat_id = call.message.chat.id
    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()
    build = CLAN_BUILDINGS[building]

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
        and build.admins_only
    ):
        return await call.answer(
            '👀 Пользоваться данной постройкой может только администратор чата',
            show_alert=True
        )

    amount = cur.select(f"build_{building}", "clandata").where(
        clan_id=chat_id).one()
    if not amount:
        return await call.answer(
            '🤨 В клане нет этой постройки, что вы собрались использовать?',
            show_alert=True
        )

    text = f"<b>{build.ru_name}</b> - {build.description}"
    if build.max_level:
        text += f".\n\nУровень постройки - <b>{amount}</b>"

    markup = InlineKeyboardMarkup(row_width=1)
    if build.shop is not None:
        for item in build.shop:
            markup.add(
                buybutton(item, status='clan')
            )

    match(building):
        case "farm":
            clan_cows = cur.select("cows", "clandata").where(
                clan_id=chat_id).one()
            user_cows = cur.select("cow", "userdata").where(
                user_id=call.from_user.id).one()
            text += (
                ".\n\n🐄 Чтобы участники клана могли доить коров, в клане "
                f"должна быть минимум одна корова. У вас <b>{user_cows}"
                f"</b> коров, в клане <b>{clan_cows}</b> коров.\n\nКаждый "
                "пользователь может доить только одну корову в день (и только"
                " в том клане, в котором он состоит). При каждой дойке из "
                "клана забирается одна корова"
            )
            markup.add(
                InlineKeyboardButton(
                    text='🐄 Пожертвовать корову в клан',
                    callback_data='donate_cow'
                ),
                InlineKeyboardButton(
                    text='🥛 Подоить корову',
                    callback_data='milk_cow_clan'
                )
            )
        case "mail":
            text += (
                ".\n\n📦 Раз в неделю администраторы группы могут раздать "
                "лутбоксы всем участникам клана. Каждому участнику выдаётся "
                "количество лутбоксов, равное уровню постройки"
            )
            markup.add(
                InlineKeyboardButton(
                    text='📦 Раздать лутбоксы',
                    callback_data='give_lootboxes'
                )
            )

    await call.message.answer(
        f"<i>{text}</i>",
        reply_markup=markup.add(
            InlineKeyboardButton(
                text="◀ Назад",
                callback_data="cancel_action"
            )
        )
    )


async def donate_cow(call: CallbackQuery) -> None:
    '''
    Callback for donating a cow to clan

    :param call - callback:
    '''
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

    user_cow = cur.select("cow", "userdata").where(
        user_id=user_id).one()
    if user_cow < 1:
        return await call.answer(
            "😣 У вас недостаточно коров. Купите хотя бы одну в зоопарке",
            show_alert=True
        )

    cur.update("userdata").add(cow=-1).where(user_id=user_id).commit()
    cur.update("clandata").add(cows=1).where(clan_id=chat_id).commit()
    clan_cow = cur.select("cows", "clandata").where(
        clan_id=chat_id).one()

    await call.answer(
        f"🥳 Вы пожертвовали корову в клан. Теперь у вас {user_cow-1}"
        f" коров, зато в клане их {clan_cow}",
        show_alert=True
    )


async def milk_cow_clan(call: CallbackQuery) -> None:
    '''
    Callback for donating a cow in a clan

    :param call - callback:
    '''
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

    has_building = cur.select("build_farm", "clandata").where(
        clan_id=chat_id).one()
    if not has_building:
        return await call.answer(
            "😣 В клане нет постройки \"Ферма\"",
            show_alert=True
        )

    last_milk = cur.select("last_milk", "userdata").where(
        user_id=user_id).one()
    if current_time()-last_milk < 86400:
        hours, minutes, seconds = get_time_units(current_time()-last_milk)
        return await call.answer(
            "🥱 Вы уже доили корову сегодня. Подождите "
            f"{hours} часов {minutes} минут {seconds} секунд",
            show_alert=True
        )

    clan_id = cur.select("clan_id", "userdata").where(
        user_id=user_id).one()
    if clan_id != chat_id:
        return await call.answer(
            "😨 Доить корову в клане могут только участники клана",
            show_alert=True
        )

    clan_cow = cur.select("cows", "clandata").where(
        clan_id=chat_id).one()
    if clan_cow < 1:
        return await call.answer(
            "😣 В клане нет коров",
            show_alert=True
        )

    await call.answer(
        "🥛 Дойка коровы началась... Подождите 10 секунд",
        show_alert=True
    )
    cur.update("userdata").set(last_milk=current_time()).where(
        user_id=user_id).commit()
    await asyncio.sleep(10)
    cur.update("userdata").add(milk=1).where(user_id=user_id).commit()
    cur.update("clandata").add(cows=-1).where(clan_id=chat_id).commit()

    await call.message.answer(
        f"<i>🐄 Участник клана <b>{await get_embedded_link(user_id)}</b> "
        "подоил корову</i>"
    )


async def give_lootboxes(call: CallbackQuery) -> None:
    '''
    Callback for sending lootboxes to clan members

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

    amount = cur.select("build_mail", "clandata").where(
        clan_id=chat_id).one()
    if not amount:
        return await call.answer(
            "😣 В клане нет постройки \"Почтовое отделение\"",
            show_alert=True
        )

    member = await bot.get_chat_member(chat_id, call.from_user.id)
    if (
        not member.is_chat_admin()
        and not member.is_chat_creator()
    ):
        return await call.answer(
            '👀 Раздавать лутбоксы может только администратор чата',
            show_alert=True
        )

    remaining = 604800-current_time()+cur.select(
        "last_lootbox", "clandata").where(clan_id=chat_id).one()
    if remaining >= 0:
        days = int(remaining // 86400)
        without_days = remaining-days*86400
        hours, minutes, seconds = get_time_units(86400-without_days)
        return await call.answer(
            f"🥱 Вы уже отправляли лутбоксы на этой неделе. Подождите {days}"
            f" дней {hours} часов {minutes} минут {seconds} секунд",
            show_alert=True
        )

    cur.update("clandata").set(last_lootbox=current_time()).where(
        clan_id=chat_id).commit()

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
    match(str(amount)[-1]):
        case "1":
            lootbox_case = "лутбокс"
        case "2" | "3" | "4":
            lootbox_case = "лутбокса"
        case _:
            lootbox_case = "лутбоксов"
    if len(str(amount)) > 1 and str(amount)[-2] == "1":
        lootbox_case = "лутбоксов"

    for member_id in clan_members:
        cur.update("userdata").add(lootbox=amount).where(
            user_id=member_id[0]).commit()
        try:
            await bot.send_message(
                chat_id=member_id[0],
                text=f'<i>📦 Вам {amount} {lootbox_case} от <b>'
                     f'<a href="{link}">{clan_name}</a></b></i>'
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
        '<i><b>📦 Раздача лутбоксов завершена</b>\n\n'
        f'✅ Сообщение успешно отправлено: <b>{sent_successfully}</b>\n'
        '🚮 Пользователи не существуют или удалены из Telegram: '
        f'<b>{user_not_exists}</b>\n✋ Заблокировали Живополис: '
        f'<b>{blocked_bot}</b>\n❌ Другие ошибки: <b>{errors}</b></i>',
        reply_markup=markup
    )


async def rob_clan(message: Message):
    '''
    Callback for clan robbing

    :param message - user's message:
    '''
    chat_id = message.chat.id
    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text='🥱 Хорошо',
            callback_data='cancel_action'
        )
    )

    if count < 1:
        return await message.reply(
            "😓 <i>Похоже, такого клана не существует</i>",
            reply_markup=markup
        )
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    balance = cur.select("clan_balance", "clandata").where(
        clan_id=chat_id).one()
    if balance > 100000:
        return await message.reply(
            "👀 <i>Нельзя взламывать кланы, баланс которых больше $100k</i>",
            reply_markup=markup
        )

    if random.randint(1, 10) < 10:
        return await prison_sentence(
            message, term=10, reason="попытку обворовать клан",
            caption="Видимо, кому-то придётся поучиться взламывать..."
        )
    if balance < 45:
        return await message.reply(
            "😣 <i>В клане почти нет денег :(</i>",
            reply_markup=markup
        )
    rob_sum = random.randint(1, 45)
    cur.update("clandata").add(clan_balance=-rob_sum).where(
        clan_id=chat_id).commit()
    cur.update("userdata").add(balance=rob_sum).where(
        user_id=message.from_user.id).commit()

    await message.answer(
        f"<i>😎 Крутой <b>{await get_embedded_link(message.from_user.id)}"
        f"</b> взломал клан и забрал <b>${rob_sum}</b></i>"
    )
