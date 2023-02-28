from aiogram.types import CallbackQuery
from aiogram import Dispatcher

from loguru import logger
from ..config import ITEMS
from ..bot import bot
from ..database.functions import create_acc, check, cur
from .callbacks.other import chats
from .callbacks.for_admins import adminpanel, itemsinfo_table, itemsinfo_item
from .callbacks.inventory import itemdesc, inventory

async def callback_handler(call: CallbackQuery):
    try:
        await check(call.from_user.id, call.message.chat.id)

        health = cur.execute(f"SELECT health FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]

        if health < 0:
            await call.answer(text='☠ Вы умерли')
            if call.message.chat.type == 'private':
                await call.message.answer('<i>&#9760; Вы умерли. Попросите кого-нибудь вас воскресить</i>', parse_mode = 'html')
                
        match (call.data):
            case 'sign_up':
                await create_acc(call.from_user, call.from_user.id)
            case 'chats':
                await chats(call.from_user.id, call.message)
            case 'adminpanel':
                await adminpanel(call, call.from_user.id)
            case 'itemsinfo_table':
                await itemsinfo_table(call, call.from_user.id)
            case 'inventory':
                await inventory(call)
            case data if data.startswith('iteminfo_'):
                await itemsinfo_item(call, call.from_user.id)
            case item if item in ITEMS:
                await itemdesc(call, call.from_user.id)
            case 'cancel_action':
                await bot.delete_message(call.message.chat.id, call.message.message_id)
            case 'no_items_in_inventory':
                await call.answer('🙉  У вас в инвентаре нет предметов. Но вы всегда можете их купить.', show_alert=True)
            case _:
                return await call.answer('command not found', show_alert=True)
    except TypeError:
        return call.answer("У вас нет учетной записи, сэр. Зарегистрируйтесь, пожалуйста", show_alert=True)
    return await call.answer('...')
        

def register(dp: Dispatcher):
    dp.register_callback_query_handler(callback_handler)