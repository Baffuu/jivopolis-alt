from aiogram.types import CallbackQuery

from ..config import ITEMS, SUPPORT_LINK
from ..bot import bot, Dispatcher

from ..database.functions import create_acc, check, cur, profile

from .callbacks.other import chats, my_refferals
from .callbacks.for_admins import adminpanel, itemsinfo_table, itemsinfo_item, adminhelp, sqlapprove, sqldecline, restart
from .callbacks.inventory import itemdesc, inventory, put_mask_off, open_lootbox

async def callback_handler(call: CallbackQuery):
    try:
        await check(call.from_user.id, call.message.chat.id)

        health = cur.execute(f"SELECT health FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]
        is_banned = bool(cur.execute(f"SELECT is_banned FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0])
        
        if is_banned:
            await call.answer(f'🧛🏻‍♂️ Вы были забаненны в боте. Если вы считаете, что это - ошибка, обратитесь в поддержку.', show_alert=True)
            return bot.send_message(call.from_user.id, f'🧛🏻‍♂️ Вы были забаненны в боте. Если вы считаете, что это - ошибка, обратитесь в <a href="{SUPPORT_LINK}">поддержку</a>.')

        if health < 0:
            await call.answer(text='☠️ Вы умерли')
            if call.message.chat.type == 'private':
                return await call.message.answer('<i>☠️ Вы умерли. Попросите кого-нибудь вас воскресить</i>', parse_mode = 'html')

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
            case 'put_mask_off':
                await put_mask_off(call, call.from_user.id)
            case 'my_refferals':
                await my_refferals(call.message, call.from_user.id)
            case 'profile':
                await profile(call.from_user.id, call.message, True)
            case 'mailbox' | 'open_lootbox':
                await open_lootbox(call.from_user.id, call.message)
            case 'adminhelp':
                await adminhelp(call, call.from_user.id)
            case sql_request if sql_request.startswith('sqlrun:'):
                if call.data.startswith('sqlrun:approve:'):
                    await sqlapprove(call)
                elif call.data.startswith('sqlrun:decline:'):
                    await sqldecline(call)
            case 'restart_bot':
                await restart(call)
            case _:
                return await call.answer('command not found', show_alert=True)
    except TypeError:
        if call.data == 'sign_up':
            await create_acc(call.from_user, call.message.chat.id)
            return #todo
        return await call.answer("🧑‍🎨 Сэр, у вас нет аккаунта в живополисе. Прежде чем использовать любые комманды вам нужно зарегистрироваться.", show_alert=True)
    return await call.answer('...')
        

def register(dp: Dispatcher):
    dp.register_callback_query_handler(callback_handler)