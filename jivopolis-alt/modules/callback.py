
# flake8: noqa
import contextlib

from .callbacks import *
from .. import bot, logger, Dispatcher, tglog, utils
from ..misc import ITEMS
from ..misc.config import SUPPORT_LINK, villages, trains
from ..database import cur
from ..database.functions import check, profile, eat
from ..filters import RequireBetaFilter

from aiogram.types import CallbackQuery


async def callback_handler(call: CallbackQuery):
    '''
    handler for all callbacks

    :param call - callback:
    '''
    try:
        with contextlib.suppress(AttributeError):
            await check(call.from_user.id, call.message.chat.id)
        health = cur.select("health", "userdata").where(
            user_id=call.from_user.id).one()
        is_banned = bool(
            cur.select("is_banned", "userdata").where(
                user_id={call.from_user.id}
            ).one()
        )

        if is_banned:
            await call.answer(
                '🧛🏻‍♂️ Вы были забанены в боте. Если вы считаете, что это '
                'ошибка, обратитесь в поддержку',
                show_alert=True,
            )
            return await bot.send_message(
                call.from_user.id,
                (
                    "🧛🏻‍♂️ <i>Вы были забанены в боте. Если вы считаете, что "
                    f"это ошибка, обратитесь в <a href='{SUPPORT_LINK}'"
                    ">поддержку</a></i>"
                ),
            )

        if health < 0:
            await call.answer(text='☠️ Вы умерли')
            if call.message.chat.type == 'private':
                return await call.message.answer(
                    '<i>☠️ Вы умерли. Попросите кого-нибудь вас воскресить</i>'
                )

        match (call.data):
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
                await call.answer('🙉  У вас в инвентаре нет предметов. Но вы всегда можете их купить', show_alert=True)
            case 'put_mask_off':
                await put_mask_off(call, call.from_user.id)
            case mask if mask.startswith('put_mask_on_'):
                await put_mask_on(call, call.data[12:])
            case 'my_refferals':
                await my_refferals(call.message, call.from_user.id)
            case 'profile':
                await profile(call.from_user.id, call.message, True)
            case 'mailbox' | 'open_lootbox':
                await lootbox_button(call.from_user.id, call.message)
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
                await city(call.message, str(call.from_user.id))  # todo refactoring
            case 'car_menu':
                await car_menu(call)
            case car if car.startswith('goto_on_car'):
                await goto_on_car(call)
            case 'local_people':
                await local_people(call)
            case cheque if cheque.startswith('check_'):
                await get_cheque(call, call.from_user.id)

            case 'phone_shop':
                await shop(
                    call,
                    place='Генерала Шелби',
                    items=['phone'],
                    text='📱 Добро пожаловать в магазин техники имени Шелби'
                )
            case 'candy_shop':
                await shop(
                    call,
                    place='Георгиевская',
                    items=[
                        'donut', 'cookie', 'chocolate', 'cake',
                        'yogurt', 'ice_cream', 'shaved_ice',
                    ],
                    text='🍰 Добро пожаловать в нашу кондитерскую!'
                )
            case 'japan_shop':
                await shop(
                    call,
                    place='ТЦ МиГ',
                    items=[
                        'bento', 'rice', 'pasta'
                    ],
                    text='🍱 Добро пожаловать в ресторан восточной кухни "Япон Енот"!'
                )
            case 'xmas_shop':
                await shop(
                    call,
                    place='',
                    items=[
                        'snowman',  'snowflake', 'xmastree',  'fairy',
                        'santa_claus',  'mrs_claus', 'firework',
                        'fireworks', 'confetti'
                    ],
                    text='🎄 Добро пожаловать в новогодний раздел магазина ModaShop!',
                )
            case 'fruit_shop':
                await shop(
                    call,
                    place='',
                    items=[
                        'apple', 'cucumber', 'tomato', 'kiwi', 'coconut'
                    ],
                    text='🍏 Добро пожаловать в мини-магазин "Натурал"!'
                )
            case 'zoo_shop':
                await shop(
                    call,
                    place='Зоопарк',
                    items=[
                        'seal', 'cow', 'hedgehog',
                        'wolf', 'fox', 'hamster'
                    ],
                    text=(
                        "🐘 Добро пожаловать в зоопарк! Здесь вы также можете"
                        " купить пару животных, у зоопарков нынче совсем денег нет…"
                        "\n\n*вы настораживаетесь* 🤔 - А это вообще легально?"
                    ),
                )
            case 'enot_kebab_shop':
                await shop(
                    call,
                    place=villages + trains[0],
                    items=[
                        'burger', 'fries', 'shaurma', 'cheburek', 'beer'
                    ],
                    text=(
                        "🍔 Добро пожаловать в закусочную Енот-Кебаб! Здесь вы найдёте лучшую еду "
                        "по лучшим ценам и абсолютно точно не отравитесь! (надеемся)"
                        "\n\n*вы замечаете надпись* ‼️ Енотов мы больше не продаём, "
                        "нам запретили разработчики!"
                    ),
                )
            case 'botan_garden_shop':
                await shop(
                    call,
                    place='Ботаническая',
                    items=[
                        'clover', 'palm', 'rose', 'tulip',
                        'houseplant', 'cactus'
                    ],
                    text=(
                        "🌲Добро пожаловать в Ботанический Сад! Сегодня у нас распродажа парочки "
                        "интересных цветов, не хотите взглянуть?"
                    )
                )
            case 'car_shop':
                await shop(
                    call,
                    place='Автопарк им. Кота',
                    items=[
                        'red_car', 'blue_car'
                    ],
                    text=(
                        "🏎 *вы слышите рёв мотора* Добро пожаловать в самый крутой автопарк в Живополисе!"
                        "\n\n🤔 *говорят, основатель этого автопарка - самый успешный кот в живополисе*"
                    ),
                )
            case 'hospital_shop':
                await shop(
                    call,
                    place=['Райбольница', 'Старокотайский ФАП'],
                    items=['pill x1', 'pill x2', 'pill x3'],
                    text="🏥 Добро не пожаловать в нашу замечательную больницу! Располагаетесь на койке и не умрите до прихода доктора."
                )
            case 'building_shop':
                await shop(
                    call,
                    place='Максименка',
                    items=['window', 'brick', 'door'],
                    text='🧱 Добро пожаловать в строительный магазин - дом любого мужчины!'
                )

            case 'moda_menu':
                await moda_menu(call)
            case 'mall':
                await mall(call)

            case 'my_reflink':
                await my_reflink(call)
            case 'cellphone_menu':
                await cellphone_menu(call)
            case 'delivery_app':
                await delivery_menu(call)
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
            case 'economics':
                await economics(call)
            case 'shop_24':
                await shop_24(call)
            case 'join_clan':
                await joinclan(call, call.from_user.id)
            case 'leave_clan':
                await leaveclan(call)
            case "create_clan":
                await create_clan(call)
            case buyclan if buyclan.startswith('buyclan_'):
                await buyclan_(call, call.data.replace('buyclan_', ''))

            case taxi if taxi.startswith("taxi_next:"):
                await taxi_next(call, int(call.data.replace("taxi_next:", "")))
            case taxi if taxi.startswith("taxi_previous:"):
                await taxi_previous(call, int(call.data.replace("taxi_previous:", "")))

            case car if car.startswith("car_menu_next:"):
                await car_menu_next(call, int(call.data.replace("car_menu_next:", "")))
            case car if car.startswith("car_menu_previous:"):
                await car_menu_previous(call, int(call.data.replace("car_menu_previous:", "")))

            case "toggle_nonick":
                await toggle_nonick(call)
            case "user_settings":
                await user_settings(call)

            case "help":
                await call.message.answer(
                    (
                        "<i><b>&#10067; Справка по игре в Живополис</b>\n"
                        "Команды бота: https://telegra.ph/Komandy-ZHivopol"
                        "isa-11-21\nКак играть: https://telegra.ph/Kak-igra"
                        "t-v-ZHivopolis-11-21</i>"
                    )
                )
            case "metro":
                await metro(call)
            case "proceed_metro":
                await proceed_metro(call)
            case "metro_forward":
                await metro_forward(call)
            case "metro_back":
                await metro_back(call)
            case "regtrain_forward":
                await regtrain_forward(call)
            case "regtrain_back":
                await regtrain_back(call)
            case "transfer":
                await transfer_metro(call)

            case "privacy_settings":
                await privacy_settings(call)
            case "work":
                await call.answer("🏗 Ведутся строительные работы. Ожидайте открытия вашей работы в ближайших обновлениях.", True)
            case "airport":
                await airport(call)
            case _flight if _flight.startswith("flight"):
                await flight(call)
            case "exchange_center":
                await exchange_center(call)
            case ex if ex.startswith("exchange_menu_"):
                await exchange_menu_(call)
            case ex if ex.startswith("exchange_"):
                await exchange_(call)
            case _:
                return await call.answer('♿️ 404: команда не найдена.', show_alert=True)
    except TypeError as e:
        logger.exception(e)
        return await call.answer("🧑‍🎨 Сэр, у вас нет аккаунта в живополисе. Прежде чем использовать любые команды вам нужно зарегистрироваться", show_alert=True)
    except Exception as e:
        await tglog(f"<b>☣️ TRACEBACK:</b> \n\n{utils.get_trace(e)}", "#traceback")
        logger.exception(e)
    return await call.answer('...')


def register(dp: Dispatcher):
    dp.register_callback_query_handler(callback_handler, RequireBetaFilter())
