
# flake8: noqa

import contextlib

from .callbacks import *
from .. import bot, logger, Dispatcher, tglog, utils
from ..misc import ITEMS
from ..misc.config import SUPPORT_LINK, villages, trains, CITY, tramroute
from ..database import cur
from ..database.functions import check, profile, eat, current_time, buy_in_oscar_shop, set_ride_status
from ..filters import RequireBetaFilter
from aiogram.utils.exceptions import (
    MessageCantBeDeleted,
    MessageToDeleteNotFound
)

from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

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
            return

        ride_status = cur.select("is_in_ride", "userdata").where(
            user_id=call.from_user.id).one()
        if ride_status and not call.data.startswith('exit_'):
            return await call.answer(
                "😡 Не пользуйтесь ботом во время поездки!",
                show_alert=True
            )

        in_prison = cur.select("prison_started", "userdata").where(
            user_id=call.from_user.id).one() - current_time()
        is_in_prison = in_prison > 0
        if is_in_prison:
            minutes = int(in_prison / 60)
            seconds = int(in_prison % 60)
            return await call.answer(
                f'👮‍♂️ Вы находитесь в тюрьме. До выхода вам осталось {minutes}'
                f' минут {seconds} секунд',
                show_alert=True
            )

        match (call.data):
            case 'chats':
                await chats(call.from_user.id, call.message)
            case 'information_menu':
                await infomenu(call)
            case 'gadget_menu':
                await gadgets_menu(call)
            case 'adminpanel':
                await adminpanel(call, call.from_user.id)
            case 'itemsinfo_table':
                await itemsinfo_table(call, call.from_user.id)
            case 'inventory':
                await inventory(call)
            case 'resources':
                await resources(call)
            case item if item.startswith('iteminfo_'):
                await itemsinfo_item(call, call.from_user.id)
            case item if item in ITEMS:
                await itemdesc(call, call.from_user.id)
            case 'cancel_action':
                await bot.delete_message(call.message.chat.id, call.message.message_id)
            case 'cancel_process':
                await bot.delete_message(call.message.chat.id, call.message.message_id)
                cur.update("userdata").set(process='').where(
                    user_id=call.from_user.id).commit()
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
            case 'city_wo_deleting':
                await city(call.message, str(call.from_user.id))
            case 'city':
                await city(call.message, str(call.from_user.id))  # todo refactoring
                with contextlib.suppress(MessageToDeleteNotFound, MessageCantBeDeleted):
                    await call.message.delete()
            case 'car_menu':
                await car_menu(call)
            case car if car.startswith('goto_on_car'):
                await goto_on_car(call)
            case 'local_people':
                await local_people(call)
            case cheque if cheque.startswith('check_'):
                await get_cheque(call, call.from_user.id)

            case 'darkweb':
                await shop(
                    call,
                    item_qualification='key',
                    items=['gun', 'poison'],
                    text='🤫 Тсс...'
                )
            case 'phone_shop':
                await shop(
                    call,
                    place=['Генерала Шелби', 'Площадь Максима'],
                    items=['phone', 'radio'],
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
                    place=['ТЦ МиГ', 'Площадь Максима'],
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
                        " купить пару животных: у зоопарков нынче совсем денег нет…"
                        "\n\n*вы настораживаетесь* 🤔 - А это вообще легально?"
                    ),
                )
            case 'enot_kebab_shop':
                await shop(
                    call,
                    place=villages + trains[0]+ ['Площадь Максима'],
                    items=[
                        'burger', 'fries', 'shaurma', 'cheburek', 'beer'
                    ],
                    text=(
                        "🍔 Добро пожаловать в закусочную Енот-Кебаб! Здесь вы найдёте лучшую еду "
                        "по лучшим ценам и абсолютно точно не отравитесь! (надеемся)"
                        "\n\n*вы замечаете надпись*\n‼️ Енотов мы больше не продаём: "
                        "нам запретили разработчики"
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
                        "🌲 Добро пожаловать в Ботанический Сад! Сегодня у нас распродажа парочки "
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
                        "\n\n🤔 *говорят, основатель этого автопарка - самый успешный кот в Живополисе*"
                    ),
                )
            case 'hospital_shop':
                await shop(
                    call,
                    place=['Райбольница', 'Старокотайский ФАП', 'Смиловичи (больница)', 'Борисовская райбольница'],
                    items=['pill x1', 'pill x2', 'pill x3'],
                    text="🏥 Добро не пожаловать в нашу замечательную больницу! Располагаетесь на койке и не умрите до прихода доктора"
                )
            case 'building_shop':
                await shop(
                    call,
                    place='Площадь Максима',
                    items=['window', 'brick', 'door'],
                    text='🧱 Добро пожаловать в строительный магазин - дом любого мужчины!'
                )
            case 'pickaxe_shop':
                await shop(
                    call,
                    place='Агзамогорск',
                    items=['pickaxe x1', 'pickaxe x2', 'pickaxe x5', 'pickaxe x10'],
                    text='⛏ Добро пожаловать в магазин шахтёра! Здесь вы можете купить себе несколько кирок для шахты'
                )
            case 'rod_shop':
                await shop(
                    call,
                    place='Морской',
                    items=['fishing_rod x1', 'fishing_rod x2', 'fishing_rod x5', 'fishing_rod x10'],
                    text='🎣 Добро пожаловать в магазин снастей! Здесь вы можете купить пару удочек для рыбалки'
                )

            case 'metro_tickets':
                await shop(
                    call,
                    items=['metrotoken x1', 'metrotoken x2', 'metrotoken x5', 'metrotoken x10'],
                    text='Здесь вы можете купить жетоны для метро'
                )
            case 'trolleybus_tickets':
                await shop(
                    call,
                    items=['trolleytoken x1', 'trolleytoken x2', 'trolleytoken x5', 'trolleytoken x10'],
                    text='Здесь вы можете купить билеты на городской троллейбус'
                )
            case 'regtrain_tickets':
                await shop(
                    call,
                    items=['regtraintoken x1', 'regtraintoken x2', 'regtraintoken x5', 'regtraintoken x10'],
                    text='Здесь вы можете купить билеты на электричку'
                )
            case 'train_tickets':
                await shop(
                    call,
                    items=['traintoken x1', 'traintoken x2', 'traintoken x5', 'traintoken x10'],
                    text='Здесь вы можете купить билеты на поезд, чтобы свалить из Живополиса'
                )
            case 'tram_tickets':
                await shop(
                    call,
                    items=['tramtoken x1', 'tramtoken x2', 'tramtoken x5', 'tramtoken x10'],
                    text='Здесь вы можете купить билеты на трамвай, чтобы путешествовать по Ридиполю'
                )

            case 'moda_menu':
                await moda_menu(call)
            case 'mall':
                await mall(call)
            case maxdom if maxdom.startswith('maximdom_floor_'):
                await maximdom(call, floor=int(maxdom[15:]))
            case 'maximdom_elevator':
                await maximdom_elevator(call)

            case 'farm':
                await farm(call)
            case 'milk_cow':
                await milk_cow(call)
            case 'mineshaft':
                await mineshaft(call)
            case 'go_mining':
                await go_mining(call)
            case 'resource_market':
                await resource_market(call)
            case 'resource_factory':
                await resource_factory(call)
            case 'process_resources':
                await process_resources(call)
            case 'fishing':
                await fishing(call)
            case 'go_fishing':
                await go_fishing(call)
            case 'fish_result':
                await fish_result(call)
            case 'factory':
                await factory(call)
            case 'play_gears':
                await play_gears(call)
            case ansgears if ansgears.startswith("answer_gears "):
                arguments = ansgears.split(' ')
                await answer_gears(
                    call, answer=arguments[1], direction=arguments[2],
                    amount=int(arguments[3])
                )
            case 'late_answer':
                await call.answer('А уже поздно, игра закончилась :(')
            case 'university':
                await university(call)
            case 'play_math':
                await play_math(call)
            case 'play_geo':
                await play_geo(call)
            case 'oscar_shop':
                await oscar_shop(call)
            case oscardept if oscardept.startswith('oscar_dept_'):
                await oscar_dept(call, oscardept.replace('oscar_dept_', ''))
            case oscarbuy if oscarbuy.startswith('oscar_buy_'):
                await buy_in_oscar_shop(call, oscarbuy.replace('oscar_buy_', ''))
            case ansmath if ansgears.startswith("answer_math "):
                arguments = ansgears.split(' ')
                await answer_math(
                    call, answer=arguments[1], number_1=int(arguments[2]),
                    operator=arguments[3], number_2=int(arguments[4]),
                    suggestion=int(arguments[5])
                )
            case ansgeo if ansgeo.startswith("answer_geo "):
                arguments = ansgeo.split(' ')
                await answer_geo(
                    call, answer=arguments[1], country=int(arguments[2]),
                    capital=int(arguments[3])
                )

            case 'my_reflink':
                await my_reflink(call)
            case 'cellphone_menu':
                await cellphone_menu(call)
            case 'radio_menu':
                await radio_menu(call)
            case 'delivery_app':
                await delivery_menu(call)
            case 'weather_forecast':
                await weather_forecast(call)
            case 'weather_forecast_radio':
                await radio_frequency(
                    call, 71, weather_forecast_radio_program()
                )
            case 'central_market_menu':
                await central_market_menu(call)
            case 'central_market_food':
                await central_market_food(call)
            case 'central_market_mask':
                await central_market_mask(call)
            case sell if sell.startswith('sellitem_'):
                await sellitem(call, call.data[9:])
            case sellres if sell.startswith('sellresource_'):
                await sellresource(call, call.data[13:])
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
            case "clan_members":
                await clan_members(call)
            case "call_clan":
                await call_clan(call)
            case "clan_top":
                await clan_top(call)
            case "clan_settings":
                await clan_settings(call)
            case "delete_clan":
                await delete_clan(call)
            case "delete_clan_confirm":
                await delete_clan_confirm(call)
            case "toggle_clan_type":
                await toggle_clan_type(call)
            case "clan_hq":
                await clan_hq(call)
            case "clan_profile":
                await clan_profile(call)
            case "set_clan_name":
                await set_clan_name(call)
            case "set_clan_bio":
                await set_clan_bio(call)
            case "set_clan_link":
                await set_clan_link(call)
            case "delete_clan_name":
                await delete_clan_name(call)
            case "delete_clan_link":
                await delete_clan_link(call)
            case "delete_clan_bio":
                await delete_clan_bio(call)
            case "set_clan_photo":
                await set_clan_photo(call)
            case "delete_clan_photo":
                await delete_clan_photo(call)
            case buy_addon if buy_addon.startswith("buyaddon_"):
                await buy_clan_addon(call, buy_addon[9:])
            case sell_addon if sell_addon.startswith("selladdon_"):
                await sell_clan_addon(call, sell_addon[10:])
            case addon if addon.startswith("addon_"):
                await clan_addon_menu(call, addon[6:])
            case "clan_features":
                await clan_features(call)
            case "set_gameclub_timeout":
                await set_gameclub_timeout(call)
            case set_timeout if set_timeout.startswith("set_timeout_"):
                await confirm_timeout(call, timeout=int(set_timeout[12:]))
            case "clan_filter":
                await clan_filter(call)
            case togglefilter if togglefilter.startswith("toggle_filter_"):
                await toggle_filter(call, filter=togglefilter[14:])
            case "clan_buildings":
                await clan_buildings(call)
            case "clan_building_shop":
                await clan_building_shop(call)

            case buildmenu if buildmenu.startswith("building_"):
                await clan_building_menu(call, buildmenu[9:])
            case buy_build if buy_build.startswith("buybuilding_"):
                await buy_clan_building(call, buy_build[12:])
            case sell_build if sell_build.startswith("sellbuilding_"):
                await sell_clan_building(call, sell_build[13:])
            case up_build if up_build.startswith("upgrade_building_"):
                await upgrade_clan_building(call, up_build[17:])
            case usebuild if usebuild.startswith("use_building_"):
                await use_clan_building(call, usebuild[13:])
            
            case "donate_cow":
                await donate_cow(call)
            case "milk_cow_clan":
                await milk_cow_clan(call)
            case "give_lootboxes":
                await give_lootboxes(call)

            case taxi if taxi.startswith("taxi_page:"):
                await taxi_page(call, int(call.data.replace("taxi_page:", "")))

            case car if car.startswith("car_menu_page:"):
                await car_menu_page(call, int(call.data.replace("car_menu_page:", "")))

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
            case "lounge":
                await regtrain_lounge(call)
            case "proceed_regtrain":
                await proceed_regtrain(call)
            case "regtrain_forward":
                await regtrain_forward(call)
            case "regtrain_back":
                await regtrain_back(call)
            case "transfer":
                await transfer_metro(call)
            case "trolleybus":
                await trolleybus_lounge(call)
            case "proceed_trolleybus":
                await proceed_trolleybus(call)
            case "trolleybus_forward":
                await trolleybus_forward(call)
            case "trolleybus_back":
                await trolleybus_back(call)
            case "trolley_stops":
                place = cur.select("current_place", "userdata").where(user_id=call.from_user.id).one()
                answer = "<b>Список остановочных пунктов:</b>\n\n🚏 - Вы находитесь здесь.\n\n"
                for stop in CITY:
                    answer += f"<b>🚏 {stop}</b>\n" if stop == place else f"{stop}\n"
                markup = InlineKeyboardMarkup()
                markup.add(
                            InlineKeyboardButton(
                            text='❌ Закрыть',
                            callback_data='cancel_action'
                          )
                )
                await call.message.answer(f"<i>{answer}</i>", reply_markup = markup)
            case "tram_stops":
                place = cur.select("current_place", "userdata").where(user_id=call.from_user.id).one()
                answer = "<b>Список остановочных пунктов трамвая:</b>\n\n🚏 - Вы находитесь здесь.\n\n"
                for stop in tramroute:
                    answer += f"<b>🚏 {stop}</b>\n" if stop == place else f"{stop}\n"
                markup = InlineKeyboardMarkup()
                markup.add(
                            InlineKeyboardButton(
                            text='❌ Закрыть',
                            callback_data='cancel_action'
                          )
                )
                await call.message.answer(f"<i>{answer}</i>", reply_markup = markup)
            case "exit_metro":
                set_ride_status(call.from_user.id, 0)
                cur.update("userdata").set(left_transport=call.message.message_id).where(user_id=call.from_user.id).commit()
                with contextlib.suppress(MessageToDeleteNotFound, MessageCantBeDeleted):
                    await call.message.delete()
                await metrocall(call)
            case "exit_regtrain":
                set_ride_status(call.from_user.id, 0)
                cur.update("userdata").set(left_transport=call.message.message_id).where(user_id=call.from_user.id).commit()
                with contextlib.suppress(MessageToDeleteNotFound, MessageCantBeDeleted):
                    await call.message.delete()
                await regtraincall(call)
            case "exit_trolleybus":
                set_ride_status(call.from_user.id, 0)
                cur.update("userdata").set(left_transport=call.message.message_id).where(user_id=call.from_user.id).commit()
                with contextlib.suppress(MessageToDeleteNotFound, MessageCantBeDeleted):
                    await call.message.delete()
                await trolleybuscall(call)
            case "exit_tram":
                set_ride_status(call.from_user.id, 0)
                cur.update("userdata").set(left_transport=call.message.message_id).where(user_id=call.from_user.id).commit()
                with contextlib.suppress(MessageToDeleteNotFound, MessageCantBeDeleted):
                    await call.message.delete()
                await tramcall(call)
            case "railway_station":
                await railway_station(call)
            case "exit_to_railway_station":
                with contextlib.suppress(MessageToDeleteNotFound, MessageCantBeDeleted):
                    await call.message.delete()
                await railway_station(call)
            case "tickets":
                await ticket_shop(call)
            case "businessclass_lounge":
                await businessclass_lounge(call)
            case train if train.startswith('go_bytrain_to_'):
                await go_bytrain(call, destination=train[14:])
            case "bus":
                await bus(call)
            case "exit_to_busstation":
                with contextlib.suppress(MessageToDeleteNotFound, MessageCantBeDeleted):
                    await call.message.delete()
                await bus(call)
            case "shuttle_lounge":
                await buscall(call)
            case "bus_lounge":
                await regbuscall(call)
            case train if train.startswith('go_bybus_to_'):
                await go_bybus(call, destination=train[12:])
            case train if train.startswith('go_byshuttle_to_'):
                await go_byshuttle(call, destination=train[16:])
            case "tram":
                await tram_lounge(call)
            case "proceed_tram":
                await proceed_tram(call)
            case "tram_forward":
                await tram_forward(call)
            case "tram_back":
                await tram_back(call)
            case walkname if walkname.startswith("walk_"):
                await walk(call, destination=walkname[5:])
            case "local_clans":
                await local_clans(call)
            case "search_by_address":
                await search_by_address(call)

            case gpscat if gpscat.startswith("gps_category_"):
                await gps_category(call, category=gpscat.replace("gps_category_", ""))
            case nogpscat if gpscat.startswith("nogps_category_"):
                await gps_category(call, category=gpscat.replace("nogps_category_", ""),
                                   nogps=True)
            case gpsloc if gpsloc.startswith("gps_location_"):
                await gps_location(call, index=int(gpsloc.replace("gps_location_", "")))
            case gpsloc if gpsloc.startswith("nogps_location_"):
                await gps_location(call, index=int(gpsloc.replace("nogps_location_", "")),
                                   nogps=True)
            case access if access.startswith("gps_transport_"):
                await gps_transport(call, place=access.replace("gps_transport_", ""))

            case "privacy_settings":
                await privacy_settings(call)
            case 'log-out':
                await log_out(call)
            case 'delete-account':
                await delete_account(call)
            case 'delete_account_confirm':
                await delete_account_confirm(call)
            case 'toggle_profile_type':
                await toggle_profile_type(call)
            case 'profile_settings':
                await profile_settings(call)
            case 'set_nick':
                await set_nick(call)
            case 'set_bio':
                await set_bio(call)
            case 'set_photo':
                await set_photo(call)
            case 'delete_nick':
                await delete_nick(call)
            case 'delete_bio':
                await delete_bio(call)
            case 'delete_photo':
                await delete_photo(call)
            
            case 'achievements':
                await achievements(call)
            case achcat if achcat.startswith('ach_category_'):
                await achievement_category(call, achcat.replace('ach_category_', ''))
            case 'owlpizza_order':
                await shop(
                    call,
                    place='Жодино',
                    items=['pizza x1', 'pizza x2', 'pizza x3', 'pizza x5'],
                    text='🍕 Добро пожаловать в лучшую в Живополисе пиццерию <b>OwlPizza</b>!'
                )
            case 'owlpizza':
                await owlpizza(call)
            case 'owlpizza_work':
                await owlpizza_work(call)
            case 'owlpizza_startwork':
                await owlpizza_startwork(call)
            case "work":
                await call.answer("🏗 Ведутся строительные работы. Ожидайте открытия вашей работы в ближайших обновлениях", True)
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
            case slot if slot.startswith("slot"):
                await buyslot(call)
            case i if i.startswith("product_info_"):
                await product_info(call)
            case _:
                return await call.answer('♿️ 404: команда не найдена', show_alert=True)
    except TypeError as e:
        logger.exception(e)
        return await call.answer("🧑‍🎨 Сэр, у вас нет аккаунта в Живополисе. Прежде чем использовать любые команды, вам нужно зарегистрироваться", show_alert=True)
    except Exception as e:
        await tglog(f"<b>☣️ TRACEBACK:</b> \n\n{utils.get_trace(e)}", "#traceback")
        logger.exception(e)
    return await call.answer('...')


def register(dp: Dispatcher):
    dp.register_callback_query_handler(callback_handler, RequireBetaFilter())
