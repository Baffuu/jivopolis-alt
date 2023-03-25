from aiogram.types import CallbackQuery

from ..config import ITEMS, SUPPORT_LINK
from .. import bot, Dispatcher, logger
from ..database.functions import create_acc, check, cur, profile, eat
from .callbacks import *

async def callback_handler(call: CallbackQuery):
    try:
        try:
            await check(call.from_user.id, call.message.chat.id)
        except AttributeError:
            pass #todo create something better
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
            case item if item.startswith('iteminfo_'):
                await itemsinfo_item(call, call.from_user.id)
            case item if item in ITEMS:
                await itemdesc(call, call.from_user.id)
            case 'cancel_action':
                await bot.delete_message(call.message.chat.id, call.message.message_id)
            case 'no_items_in_inventory':
                await call.answer('🙉  У вас в инвентаре нет предметов. Но вы всегда можете их купить.', show_alert=True)
            case 'put_mask_off':
                await put_mask_off(call, call.from_user.id)
            case mask if mask.startswith('put_mask_on_'):
                await put_mask_on(call, call.data[12:])
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
            case 'set_user_bio':
                await set_user_bio(call)
            case food if food.startswith('eat_'):
                await eat(call, call.data[4:])
            case buy if buy.startswith('buy_'):
                await buycall(call)
            case 'adminchats':
                await adminchats(call)
            case 'city':
                await city(call.message, call.from_user.id) #todo refactoring
            case 'car_menu':
                await car_menu(call)
            case car if car.startswith('goto_on_car'):
                await goto_on_car(call)
            case 'local_people':
                await local_people(call)
            case cheque if cheque.startswith('check_'):
                await get_cheque(call, call.from_user.id)
            case 'phone_shop':
                await phone_shop(call)
            case 'candy_shop':
                await candy_shop(call)
            case 'japan_shop':
                await japan_shop(call)
            case 'mall':
                await mall(call)
            case 'moda_shop':
                await moda_shop(call)
            case 'xmas_shop':
                await xmas_shop(call)
            case 'enot_kebab_shop':
                await enot_kebab_shop(call)
            case 'my_reflink':
                await my_reflink(call)
            case 'cellphone_menu':
                await cellphone_menu(call)
            case 'delivery_app':
                await delivery_menu(call)
            case 'fruit_shop':
                await fruit_shop(call)
            case 'central_market_menu':
                await central_market_menu(call)
            case 'central_market_food':
                await central_market_food(call)
            case 'central_market_mask':
                await central_market_mask(call)
            case sell if sell.startswith('sellitem_'):
                await sellitem(call, call.data[9:])
            case 'bank':
                await bank(call)
            case 'state_balance':
                await state_balance(call)
            case state if state.startswith('give_state'):
                await give_state(call, call.data[9:])
            case 'taxi_menu':
                await taxi_menu(call.message, call.from_user.id)
            case taxi if taxi.startswith('taxicost_'):
                await taxicost(call, call.data[9:])
            case taxi if taxi.startswith('taxi_goto_'):
                await taxi_goto_(call, call.data[10:])
            case 'gps':
                await gps_menu(call)
            case buy24 if buy24.startswith('buy24_'):
                await buy24_(call, call.data[6:])
            case 'zoo_shop':
                await zoo_shop(call)
            case 'economics':
                await economics(call)
            case 'shop_24':
                await shop_24(call)
            case 'join_clan':
                await joinclan(call, call.from_user.id)
            case "create_clan":
                await create_clan(call)
            case buyclan if buyclan.startswith('buyclan_'):
                await buyclan_(call, call.data.replace('buyclan_', ''))
            case _:
                return await call.answer('♿️ 404: команда не найдена.', show_alert=True)
    except TypeError as e:
        logger.exception(e)
        if call.data == 'sign_up':
            await create_acc(call.from_user, call.message.chat.id)
            return await call.answer('☁️ Записываем ваши данные…')
        return await call.answer("🧑‍🎨 Сэр, у вас нет аккаунта в живополисе. Прежде чем использовать любые комманды вам нужно зарегистрироваться.", show_alert=True)
    except Exception as e:
        logger.exception(e)
    return await call.answer('...')
        
def register(dp: Dispatcher):
    dp.register_callback_query_handler(callback_handler)