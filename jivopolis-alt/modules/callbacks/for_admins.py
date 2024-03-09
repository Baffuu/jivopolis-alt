import sys
import os

from ... import bot
from ...misc.config import (
    BAFFUADM,
    MEGACHATLINK
)
from ...misc import OfficialChats, ITEMS

from ...database import cur, conn

from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


async def adminpanel(call: CallbackQuery, user_id: int) -> None:
    '''
    Callback for admin panel

    :param call - callback:
    :param user_id:
    '''
    rank = cur.select("rank", "userdata").where(user_id=user_id).one()

    if rank < 2:
        return await call.answer(
            "❌ Эта команда доступна только администраторам Живополиса",
            show_alert=True
        )

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(
            text='❓ Admin help',
            callback_data='adminhelp'
        ),
        InlineKeyboardButton(
            text='💼 Item info',
            callback_data='itemsinfo_table'
        ),
        InlineKeyboardButton(
            text='📁 Source code',
            callback_data='backup'
        ),
        InlineKeyboardButton(
            text='💬 Admin chats',
            callback_data='adminchats'
        )
    )

    if rank > 2:
        markup.add(
            InlineKeyboardButton(
                text='♻️ Restart bot',
                callback_data='restart_bot'
            )
        )
    await call.message.answer(
        "<i>These features are admin only. Shhh...</i>",
        reply_markup=markup
    )


async def itemsinfo_table(call: CallbackQuery, user_id: int) -> None:
    '''
    Callback for table with buttons, which contains info about all items

    :param call - callback:
    :param user_id:
    '''
    rank = cur.select("rank", "userdata").where(user_id=user_id).one()

    if rank < 2:
        return await call.answer(
            "❌ Эта команда доступна только администраторам Живополиса",
            show_alert=True
        )

    markup = InlineKeyboardMarkup(row_width=10)

    items = [
        InlineKeyboardButton(
            text=ITEMS[item].emoji, callback_data=f'iteminfo_{item}'
        )
        for item in ITEMS
    ]

    markup.add(*items)

    await call.message.answer(
        "<i>Here you can get some secret info about all items in"
        " Jivopolis</i>",
        reply_markup=markup
    )


async def itemsinfo_item(call: CallbackQuery, user_id: int) -> None:
    '''
    Callback for sending info about items

    :param call - callback:
    :param user_id:
    '''
    item = call.data.split('_')[1]

    if item not in ITEMS:
        return

    rank = cur.select("rank", "userdata").where(user_id=user_id).one()

    if rank < 2:
        return await call.answer(
            "❌ Эта команда доступна только администраторам Живополиса",
            show_alert=True
        )

    await call.answer(
        f'{ITEMS[item].emoji}{ITEMS[item].ru_name}\nColumn: {item}\nType:'
        f' {ITEMS[item].type}\nPrice: ${ITEMS[item].price}',
        show_alert=True
    )


async def adminhelp(call: CallbackQuery, user_id: int) -> None:
    '''
    Callback for admin help message

    :param call - callback:
    :param user_id:
    '''
    rank = cur.select("rank", "userdata").where(user_id=user_id).one()

    if rank < 2:
        return await call.answer(
            "👨‍⚖️ Сударь, эта команда доступна только администраторам",
            show_alert=True
        )

    return await call.message.answer(
        (
            "<i><b>Admin articles</b>\nAdmin documentation: https://"
            "telegra.ph/Administratorskaya-dokumentaciya-ZHivopolisa-01-03\n"
            "<code>.sqlrun</code> usage: https://telegra.ph/Administra"
            "torskaya-dokumentaciya-ZHivopolisa-Komanda-sqlrun-07-25</i>"
        )
    )


async def sqlapprove(call: CallbackQuery) -> None:
    '''
    Callback for sql query approve

    :param call - callback:
    '''
    try:
        request_user_id = call.data.split(':')[2]
        user_id = call.from_user.id
        rank = cur.select("rank", "userdata").where(user_id=user_id).one()

        if rank < 3:
            return call.answer(
                '👨‍⚖️ Сударь, эта команда доступна только администраторам',
                how_alert=True)

        request: str = cur.select("sql", "userdata").where(
            user_id=request_user_id).one()

        if not request:
            return call.answer("404: request not found")

        cur.update("userdata").set(sql=None).where(
            user_id=request_user_id).commit()

        await bot.send_message(
            user_id,
            f'✅ <i>Your query has been approved:\n\n<code>{request}</code></i>'
        )

        cur.execute(request)
        if "select" not in request.lower():
            return conn.commit()

        try:
            await _selection(call, request_user_id, user_id, cur.fetchall())
        except Exception as e:
            await call.message.answer(
                '<i><b>An insignificant error has occured during SQL query:'
                f'</b> {e}</i>'
            )
            await call.message.answer('<i>Query has been processed</i>')

            if request_user_id != user_id:
                await bot.send_message(
                    request_user_id,
                    '<i>Query has been processed</i>'
                )

    except Exception as e:
        await call.message.answer(
            f'<i><b>Query was never processed: \n</b>{e}</i>'
        )

        if request_user_id != user_id:
            await bot.send_message(
                request_user_id,
                f'<i><b>Query was never processed: \n</b>{e}</i>'
            )


async def _selection(
    call: CallbackQuery,
    request_user_id: str | int,
    user_id: int | str,
    values: list
):
    rval = ''

    for row in values:
        for slot in row:
            rval = f"{rval}\n{str(slot)}"

    await call.message.answer(f'<i><b>Values: \n</b>{rval}</i>')

    if request_user_id != user_id:
        await bot.send_message(
            request_user_id,
            f'<i><b>Values: \n</b>{rval}</i>'
        )


async def sqldecline(call: CallbackQuery) -> None:
    '''
    Callback for sql query decline

    :param call - callback:
    :param user_id:
    '''
    try:
        request_user_id = call.data.split(':')[2]
        user_id = call.from_user.id
        rank = cur.select("rank", "userdata").where(user_id=user_id).one()

        if rank < 3:
            return call.answer(
                '👨‍⚖️ Сударь, эта команда доступна только администраторам',
                show_alert=True
            )

        request = cur.select("sql", "userdata").where(
            user_id=request_user_id).one()

        cur.update("userdata").set(sql=None).where(
            user_id=request_user_id).commit()

        await call.answer('Query declined', show_alert=True)
        await bot.send_message(request_user_id,
                               '❌ <i>Your request was declined by a megaadmin:'
                               f'\n\n<code>{request}</code></i>')
        return await bot.delete_message(call.message.chat.id,
                                        call.message.message_id)

    except Exception as e:
        return await call.message.answer(f'<i><b>&#10060; Ошибка: </b>{e}</i>')


async def adminchats(call: CallbackQuery) -> None:
    user_id = call.from_user.id
    rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={user_id}").\
        fetchone()[0]

    markup = InlineKeyboardMarkup(row_width=1)

    if rank < 1:
        return await call.answer("👨‍⚖️ Сударь, эта команда доступна только"
                                 " администраторам.", show_alert=True)
    if rank > 0:
        markup.add(InlineKeyboardButton('👾 Jivopolis testing',
                                        OfficialChats.BETATEST_CHATLINK),
                   InlineKeyboardButton('📣 Jivopolis staff',
                                        OfficialChats.JIVADM_CHATLINK),
                   InlineKeyboardButton('👨‍🔧 LOG CHAT',
                                        OfficialChats.LOGCHATLINK))
    if rank > 1:
        markup.add(InlineKeyboardButton('🧞 Baffu staff', BAFFUADM))
    if rank > 2:
        markup.add(InlineKeyboardButton('🦹🏼 Megaadmins', MEGACHATLINK))

    await call.message.answer_sticker(
        'CAACAgIAAxkBAAIEN2QE3dP0FVb2HNOHw1QC2TMpUEpsAAK7IAACEkDwSZtWAAEk4'
        '1obpC4E'
    )
    await call.message.answer("<i><b>🧑‍💻 Jivopolis admin-only chats:</b>\n"
                              "💻 Jivopolis development: "
                              "https://t.me/+k2LZEIyZtpRiMjcy</i>",
                              reply_markup=markup)


async def restart(call: CallbackQuery) -> None:
    try:
        rank = cur.execute("SELECT rank FROM userdata WHERE user_id = "
                           f"{call.from_user.id}").fetchone()[0]

        if rank < 3:
            return await call.answer("👨‍⚖️ Сударь, эта команда доступна"
                                     " только администраторам.",
                                     show_alert=True)

        await call.answer("🌀 Restarting...")
        os.execv(sys.executable, ['python3'] + sys.argv)

    except Exception as e:
        await call.message.answer(f'<i><b>♨️ Error: </b>{e}</i>')
