from ... import bot
from ...misc import ITEMS, ACHIEVEMENTS
import sqlite3
from ...database import cur
from ...database.functions import tglog, get_embedded_link

from aiogram.utils.deep_linking import get_start_link
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery, Message
)


async def set_user_bio(call: CallbackQuery) -> None:
    cur.update("userdata").set(process="setbio").where(
        user_id=call.from_user.id).commit()

    await bot.send_message(
        call.message.chat.id,
        "<i>📝 Введите новое описание профиля:</i>",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="🚫 Отмена",
                callback_data="cancel_process"
            )
        )
    )


async def put_mask_off(
    call: CallbackQuery,
    user_id: int,
    anon: bool = False
) -> None:
    if mask := cur.execute(
        f"SELECT mask FROM userdata WHERE user_id={user_id}"
    ).fetchone()[0]:
        if mask is None:
            return

        for item in ITEMS:
            if ITEMS[item].emoji == mask and ITEMS[item].type == "mask":
                mask = item

        cur.update("userdata").set(mask="NULL").where(user_id=user_id).commit()
        try:
            cur.update("userdata").add(**{mask: 1}).where(
                user_id=user_id).commit()
        except sqlite3.OperationalError:
            await call.message.answer("‼️ Your mask does not exist")
        if not anon:
            return await call.answer("🦹🏼 Ваша маска снята.", show_alert=True)


async def put_mask_on(call: CallbackQuery, item: str) -> None:
    user_id = call.from_user.id

    await put_mask_off(call, user_id, True)
    itemcount = cur.select(item, "userdata").where(user_id=user_id).one()

    if itemcount > 0:
        cur.update("userdata").add(**{item: -1}).where(
            user_id=user_id).commit()

        cur.update("userdata").set(mask=ITEMS[item].emoji).where(
            user_id=user_id).commit()

        return await call.answer(
            f"Отличный выбор! Ваша маска: {ITEMS[item].emoji}",
            show_alert=True
        )
        # await achieve(a, message.chat.id, "msqrd")
    else:
        await call.answer(
            "🚫 У вас нет этого предмета",
            show_alert=True
        )


async def my_reflink(call: CallbackQuery) -> None:
    color = '0-0-0'
    bgcolor = '255-255-255'

    reflink = await get_start_link(
        payload=str(call.from_user.id),
        encode=True
    )

    await bot.send_photo(
        call.message.chat.id,
        photo=(
            f"https://api.qrserver.com/v1/create-qr-code/?data={reflink}&"
            "size=512x512&charset-source=UTF-8&charset-target=UTF-8"
            f"&ecc=L&color={color}&bgcolor={bgcolor}&margin=1&qzone=1&format="
            "png"
        ),
        caption=(
            f"<i>Ваша реферальная ссылка: <b>{reflink}</b>\n\n"
            "За каждого приглашённого пользователя вы получаете 1 "
            "<b>📦 Лутбокс</b></i>"
        ),
    )


async def privacy_settings(call: CallbackQuery):
    markup = InlineKeyboardMarkup(row_width=1)
    user_id = call.from_user.id
    profile_type = cur.select("profile_type", "userdata").where(
        user_id=user_id).one()
    markup.add(
        InlineKeyboardButton(
            f"🔐 Тип профиля: {'Открытый' if profile_type == 'public' else 'Закрытый'}",  # noqa
            callback_data="toggle_profile_type"
        ),
        InlineKeyboardButton(
            "🔑 Ключ доступа",
            callback_data="access-key"
        ),
        InlineKeyboardButton(
            "🔙 Выйти из аккаунта",
            callback_data="log-out"
        ),
        InlineKeyboardButton(
            "🗑 Удалить аккаунт",
            callback_data="delete-account",
        ),
        InlineKeyboardButton(
            "◀ Назад",
            callback_data="cancel_action",
        )
    )
    await call.message.answer(
        '🔏<i><b>Настройки конфиденциальности</b></i>',
        reply_markup=markup
    )


async def delete_account(call: CallbackQuery):
    """
    Callback for account deleting menu

    :param call - callback:
    """

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='✅ Подтвердить',
            callback_data='delete_account_confirm'
        ),
        InlineKeyboardButton(
            text='❌ Отмена',
            callback_data='cancel_action'
        )
    )

    await call.message.answer(
        '<i>😨 Вы точно хотите удалить ваш аккаунт вместе со всеми его '
        'деньгами, ресурсами, достижениями? Это действие невозможно '
        'отменить</i>',
        reply_markup=markup
    )


async def delete_account_confirm(call: CallbackQuery):
    """
    Callback for account removal

    :param call - callback:
    """
    user_id = call.from_user.id

    embedded_link = await get_embedded_link(user_id)
    cur.execute(
        f"DELETE FROM userdata WHERE user_id={user_id}"
    ).commit()

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='😪 Хорошо',
            callback_data='cancel_action'
        ),
        InlineKeyboardButton(
            text='➕ Создать новый',
            callback_data='sign_up'
        )
    )
    await call.message.answer(
        '<i>😥 Вот и всё... Ваш аккаунт удалён. Вернуть его невозможно</i>',
        reply_markup=markup
    )

    await tglog(
            message=(
                f"😪 <b>{embedded_link}</b> удалил свой аккаунт"
            ),
            tag='#delete_account'
    )


async def log_out(call: CallbackQuery):
    """
    Callback for logging out

    :param call - callback:
    """
    user_id = call.from_user.id

    embedded_link = await get_embedded_link(user_id)
    id = cur.select("id", "userdata").where(user_id=user_id).one()
    cur.update("userdata").set(user_id=0).where(id=id).commit()

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='😪 Хорошо',
            callback_data='cancel_action'
        )
    )
    await call.message.answer(
        '<i>🥱 Вы вышли из аккаунта. Надеемся, что вы вспомните свой ключ'
        ' доступа, если вдруг вам захочется вернуть свой аккаунт</i>',
        reply_markup=markup
    )

    await tglog(
            message=(
                f"➡ <b>{embedded_link}</b> вышел из аккаунта"
            ),
            tag='#log_out'
    )


async def toggle_profile_type(call: CallbackQuery):
    """
    Callback for a clan type changing setting

    :param call - callback:
    """
    user_id = call.from_user.id

    old_type = cur.select("profile_type", "userdata").where(
        user_id=user_id).one()
    new_type = 'public' if old_type == 'private' else 'private'
    new_type_ru = 'Открытый' if new_type == 'public' else 'Закрытый'

    cur.update("userdata").set(profile_type=new_type).where(
        user_id=user_id).commit()

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='✅ Готово',
            callback_data='cancel_action'
        )
    )
    await call.message.answer(
        f'<i>🥳 Тип вашего профиля изменён на <b>{new_type_ru}</b></i>',
        reply_markup=markup
    )


async def profile_settings(call: CallbackQuery):
    """
    Callback for user profile settings

    :param call - callback:
    """
    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='✏ Изменить ник',
            callback_data='set_nick'
        ),
        InlineKeyboardButton(
            text='📝 Изменить описание',
            callback_data='set_bio'
        ),
        InlineKeyboardButton(
            text='🖼 Изменить фото профиля',
            callback_data='set_photo'
        ),
        InlineKeyboardButton(
            text='◀ Назад',
            callback_data='cancel_action'
        )
    )

    await call.message.answer(
        '<i>✏ Настройки профиля</i>',
        reply_markup=markup
    )


async def set_nick(call: CallbackQuery) -> None:
    '''
    Callback for nickname setting

    :param call - callback*
    '''
    cur.update("userdata").set(process="set_nick").where(
        user_id=call.from_user.id).commit()

    await call.message.answer(
        "<i>✏ Введите новый ник</i>",
        reply_markup=InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(
                text="🔄 По умолчанию",
                callback_data="delete_nick"
            ),
            InlineKeyboardButton(
                text="🚫 Отмена",
                callback_data="cancel_process"
            )
        )
    )


async def delete_nick(call: CallbackQuery) -> None:
    '''
    Callback for nickname resetting

    :param call - callback:
    '''
    cur.update("userdata").set(process="").where(
        user_id=call.from_user.id).commit()
    cur.update("userdata").set(nickname=call.from_user.first_name).where(
        user_id=call.from_user.id).commit()

    await call.message.answer(
        "<i>👌 Ник успешно изменён</i>",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="✅ Готово",
                callback_data="cancel_action"
            )
        )
    )


async def set_bio(call: CallbackQuery) -> None:
    '''
    Callback for nickname setting

    :param call - callback:
    '''
    cur.update("userdata").set(process="set_bio").where(
        user_id=call.from_user.id).commit()

    await call.message.answer(
        "<i>📝 Введите новое описание</i>",
        reply_markup=InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(
                text="🗑 Удалить описание",
                callback_data="delete_bio"
            ),
            InlineKeyboardButton(
                text="🚫 Отмена",
                callback_data="cancel_process"
            )
        )
    )


async def delete_bio(call: CallbackQuery) -> None:
    '''
    Callback for bio deletting

    :param call - callback:
    '''
    cur.update("userdata").set(process="").where(
        user_id=call.from_user.id).commit()
    cur.update("userdata").set(description="").where(
        user_id=call.from_user.id).commit()

    await call.message.answer(
        "<i>👌 Описание успешно удалено</i>",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="✅ Готово",
                callback_data="cancel_action"
            )
        )
    )


async def set_photo(call: CallbackQuery) -> None:
    '''
    Callback for profile picture setting

    :param call - callback:
    '''
    cur.update("userdata").set(process="set_photo").where(
        user_id=call.from_user.id).commit()

    await call.message.answer(
        "<i>📝 Отправьте новое фото профиля (в сжатом виде) или "
        "ссылку на фото</i>",
        reply_markup=InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(
                text="🗑 Удалить фото профиля",
                callback_data="delete_photo"
            ),
            InlineKeyboardButton(
                text="🚫 Отмена",
                callback_data="cancel_process"
            )
        )
    )


async def delete_photo(call: CallbackQuery) -> None:
    '''
    Callback for profile picture deletting

    :param call - callback:
    '''
    cur.update("userdata").set(process="").where(
        user_id=call.from_user.id).commit()
    cur.update("userdata").set(photo_id="").where(
        user_id=call.from_user.id).commit()

    await call.message.answer(
        "<i>👌 Фото профиля успешно удалено</i>",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="✅ Готово",
                callback_data="cancel_action"
            )
        )
    )


async def confirm_profile_setting(message: Message, setting: str) -> None:
    '''
    Callback for changing a profile setting

    :param message - message:
    :param setting - the setting to be changed:
    '''
    cur.update("userdata").set(**{setting: message.text}).where(
        user_id=message.from_user.id).commit()

    await message.answer(
        "<i>🥳 Данные профиля успешно изменены</i>",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="✅ Готово",
                callback_data="cancel_action"
            )
        )
    )


async def confirm_photo(message: Message) -> None:
    '''
    Callback for changing profile picture

    :param message - message:
    '''
    failure_markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text='😪 Хорошо',
            callback_data='cancel_action'
        )
    )

    if len(message.photo) == 0:
        new_photo = message.text
    else:
        new_photo = message.photo[0].file_id

    try:
        await message.answer_photo(
            new_photo,
            "<i>🥳 Фото успешно изменено</i>",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(
                    text="✅ Готово",
                    callback_data="cancel_action"
                )
            )
        )
        cur.update("userdata").set(photo_id=new_photo).where(
            user_id=message.from_user.id).commit()
    except Exception:
        await message.answer(
            '😨 <i>Видимо, вы отправили не фото и не ссылку на фото</i>',
            reply_markup=failure_markup.add(
                InlineKeyboardButton(
                    text='🔄 Заново',
                    callback_data='set_photo'
                )
            )
        )


async def achievements(call: CallbackQuery) -> None:
    '''
    Callback for achievement categories

    :param message - message:
    '''
    markup = InlineKeyboardMarkup(row_width=1)
    categories = []
    for achievement in ACHIEVEMENTS:
        if achievement.category not in categories:
            categories.add(
                InlineKeyboardButton(
                    text=achievement.category,
                    callback_data=f"ach_category_{achievement.category}"
                )
            )

    markup.add(*categories)
    markup.add(
        InlineKeyboardButton(
            text="◀ Назад",
            callback_data="cancel_action"
        )
    )

    await call.message.answer(
        "<i>💡 Выберите категорию достижений</i>",
        reply_markup=markup
    )


async def achievement_category(call: CallbackQuery, category: str) -> None:
    '''
    Callback for achievements in a category

    :param message - message:
    :param category - achievement category:
    '''
    user_id = call.from_user.id
    achievements = [achievement for achievement in ACHIEVEMENTS
                    if achievement.category == category]
    achievement_str = ''
    for ach in achievements:
        has_ach = cur.select(ach.name, "userdata").where(user_id=user_id).one()
        name = f"✔ {ach.ru_name}" if has_ach else ach.ru_name
        achievement_str += (
            f'\n\n<b>{name}</b>\n{ach.description}\n\n<b>Награда:'
        )
        if ach.money_reward:
            achievement_str += f'\n\t${ach.money_reward}'
        if ach.xp_reward:
            achievement_str += f'\n\t💡 {ach.xp_reward} очков'
        if ach.special_reward:
            emoji = ITEMS[ach.special_reward].emoji
            achievement_str += f'\n\t1 {emoji}'

        if not has_ach and ach.progress:
            progress = cur.select(ach.progress, "userdata").\
                where(user_id=user_id).one()
            achievement_str += f'\n\nПрогресс: {progress}/{ach.min_progress}'

        achievement_str += "\b\n\n\n"

    await call.message.answer(
        f"💡 <i>Достижения из категории <b>{category}</b>:\n\nВыполненные"
        f" достижения отмечаются символом ✔\n\n{achievement_str}</i>"
    )
