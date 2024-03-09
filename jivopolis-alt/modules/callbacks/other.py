import time
import contextlib
from math import floor
from datetime import datetime, timezone
from .traveling import state_balance

from ... import bot, logger
from ...database import cur, conn
from ...database.functions import (
    get_weather, str_weather, month, current_time, cancel_button
)
from ...misc.config import limited_items
from ...misc import get_mask, get_link, OfficialChats, get_embedded_link, ITEMS

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message, CallbackQuery
)
from aiogram.utils.exceptions import (
    MessageCantBeDeleted,
    MessageToDeleteNotFound
)
from ..._world_updater import get_crypto
from ...utils import is_allowed_nonick


async def chats(user_id: int, message: Message) -> None:
    '''
    Callback for chats

    :param user_id:
    :param message:
    '''
    rase = cur.select("rase", "userdata").where(user_id=user_id).one()
    markup = InlineKeyboardMarkup()

    match(rase):
        case "🐱":
            info = ("Расовый чат Котов",
                    "https://t.me/joinchat/mWs48dy5cAo1ZmEy")
        case "🐶":
            info = ("Расовый чат Собак",
                    "https://t.me/joinchat/yQ8X_uD1MydmNWIy")
        case "&#129437":
            info = ("Расовый чат Енотов",
                    "https://t.me/joinchat/vuVCKuUIB2gxZTYy")
        case "&#128056;":
            info = ("Расовый чат Жаб",
                    "https://t.me/joinchat/ACneINZ0hl43YTUy")
        case "&#129417;":
            info = ("Расовый чат Сов",
                    "https://t.me/joinchat/nCt9oB_cX8I3NzMy")
        case _:
            info = None

    if info is not None:
        markup.add(InlineKeyboardButton(text=info[0], url=info[1]))
    else:
        markup.add(
            InlineKeyboardButton(
                text="Выбрать расу",
                callback_data="change_rase"
            )
        )

    markup.add(
        InlineKeyboardButton(
            text="🎮 Игровой клуб",
            url="https://t.me/+2UuPwVyac6lkYjRi"
        )
    )

    await message.answer(
        "<i><b>Официальные чаты Живополиса</b>\n&#128221; Приёмная для идей и"
        "вопросов:https://t.me/zhivolab\n&#128172; Чат для общения: https://t"
        ".me/chatzhivopolisa\n&#128163; Чат для флуда: https://t.me/jivopolis"
        "_flood\n&#128176; Рынок Живополиса: t.me/jivopolis_bazar\n&#128572; "
        "Посольство Живополиса в Котостане: https://t.me/posolstvo_jivopolis_"
        "in_kotostan\n{0}".format(
            "Вы ещё не выбрали себе расу. Чтобы выбрать, нажми"
            "те на кнопку \"Выбрать расу\"\n" if info is None else ""
        ),
        reply_markup=markup
    )


async def my_refferals(message: Message, user_id: int):
    '''
    Callback for user refferals

    :param message:
    :param user_id:
    '''
    user_mask = get_mask(user_id)
    nick = cur.select("nickname", "userdata").where(user_id=user_id).one()
    count = cur.select("count(*)", "userdata").where(inviter_id=user_id).one()
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text="🖇 Реферальная ссылка",
            callback_data="reflink"
        )
    )

    if count < 1:
        return await message.answer(
            f"<i><b><a href=\"tg://user?id={user_id}\">{user_mask}{nick}</a></"
            "b>, вы пока никого не пригласили в Живополис :(</i>",
            reply_markup=markup
        )

    cur.execute(
        f"""
            SELECT * FROM userdata
            WHERE refid = {user_id}
            ORDER BY -lastseen
            LIMIT 100
        """
    )

    users = str()

    for ref_num, row in enumerate(cur, start=1):
        mask = get_mask(row[1])
        users += (
            f"\n{ref_num}. <a href = \""
            f"{await get_link(row[1])}\">{mask}{row[7]}</a>"
        )

    await message.answer(
        text=(
            "<i>&#128100; Пользователи, привлечённые <b><a href=\"tg://user"
            f"?id={user_id}\">{user_mask}{nick}</a></b>: <b>{users}</b></i>"
        ),
        reply_markup=markup
    )


async def get_cheque(call: CallbackQuery, user_id: int) -> None:
    money = int(call.data[6:])
    mask = get_mask(user_id)
    nick = cur.select("nickname", "userdata").where(user_id=user_id).one()

    cur.update("userdata").add(balance=money).where(user_id=user_id).commit()

    if not call.message:
        await bot.edit_message_text(
            inline_message_id=call.inline_message_id,
            text=(
                f"<i><b><a href=\"{await get_link(user_id)}\">{mask}{nick}</a"
                f"></b> забрал <b>${money}</b></i>"
            )
        )
    else:
        await bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=(
                f"<i><b><a href=\"{await get_link(user_id)}\">{mask}{nick}<"
                f"/a></b> забрал <b>${money}</b></i>"
            )
        )
    if money > 0:
        await bot.send_message(
            OfficialChats.LOGCHAT,
            f"<i><b>{await get_embedded_link(user_id)}</b> забрал <b>${money}<"
            "/b>\n#user_getcheck</i>"
        )


async def cellphone_menu(call: CallbackQuery) -> None:
    '''
    Callback for cell phone menu

    :param call - callback:
    :param user_id:
    '''
    phone = cur.select("phone", "userdata").where(
        user_id=call.from_user.id).one()

    if phone < 1:
        return await call.answer(
            "Вам нужен телефон. Его можно купить в магазине на ул. Генерала "
            "Шелби и одноимённой станции метро или в торговом центре в "
            "Максиграде",
            show_alert=True
        )

    markup = InlineKeyboardMarkup(row_width=1)
    weather = str_weather(get_weather())

    markup.add(
        InlineKeyboardButton(
            text="📡 GPS",
            callback_data="gps"
        ),
        InlineKeyboardButton(
            text="🚚 МиГ.Доставка",
            callback_data="delivery_app"
        ),
        InlineKeyboardButton(
            text="🚂 ЖивГорТранс: Билеты",
            callback_data="tickets"
        ),
        InlineKeyboardButton(
            text=f"{weather[0]} Прогноз погоды",
            callback_data="weather_forecast"
        ),
        InlineKeyboardMarkup(
            text="◀ Назад",
            callback_data="cancel_action"
        )
    )

    now = datetime.now(timezone.utc)

    # a function that adds 0 to the beginning of a number
    # if it has less than 2 digits
    def f(x):
        return x if len(str(x)) > 1 else f"0{x}"

    str_date = f"{f(now.day)}.{f(now.month)}.{now.year}"
    str_time = f"{f(now.hour)}:{f(now.minute)}"
    await call.message.answer(
        "<i>📱 Телефон - это удобная и современная вещь.\n\n"
        f"Сейчас: <b>{str_time}</b> (UTC), <b>{str_date}</b>\n"
        f"Погода в данный момент: <b>{weather}</b></i>",
        reply_markup=markup
    )


async def radio_menu(call: CallbackQuery) -> None:
    '''
    Callback for radio menu

    :param call - callback:
    :param user_id:
    '''
    radio = cur.select("radio", "userdata").where(
        user_id=call.from_user.id).one()

    if radio < 1:
        return await call.answer(
            "Вам нужен приёмник. Его можно купить в магазине на ул. Генерала "
            "Шелби и одноимённой станции метро или в торговом центре в "
            "Максиграде",
            show_alert=True
        )

    markup = InlineKeyboardMarkup(row_width=1)
    weather = str_weather(get_weather())

    markup.add(
        InlineKeyboardButton(
            text=f"1. {weather[0]} Прогноз погоды",
            callback_data="weather_forecast"
        ),
        InlineKeyboardMarkup(
            text="◀ Назад",
            callback_data="cancel_action"
        )
    )

    await call.message.answer(
        "<i>📻 К какой радиостанции хотите подключиться?</i>",
        reply_markup=markup
    )


async def weather_forecast(call: CallbackQuery) -> None:
    '''
    Callback for weather forecast phone app

    :param user_id:
    '''
    phone = cur.select("phone+radio", "userdata").where(
        user_id=call.from_user.id).one()

    if phone < 1:
        return await call.answer(
            'Вам нужен телефон или радио. Их можно купить в магазине'
            ' на ул. Генерала Шелби и одноимённой станции метро или в '
            'торговом центре в Максиграде',
            show_alert=True
        )

    weather_texts = ''
    int_time = current_time()
    for _ in range(6):
        now = datetime.fromtimestamp(int_time)
        weather_texts += (
            f"\n<b>{now.day} {month(now.month)}</b> - "
            f"{str_weather(get_weather(int_time))}"
        )
        int_time += 86400

    await call.message.answer(
        f"<i><b>Погода на ближайшие 7 дней:</b>\n{weather_texts}\n\n"
        "<b>!!</b> Погода изменяется в 00:00 UTC каждый день</i>",
        reply_markup=InlineKeyboardMarkup().add(
            cancel_button()
        )
    )


async def give_state(call: CallbackQuery, amount) -> None:
    '''
    Callback for clan joining

    :param call - callback:
    :param user_id:
    '''
    amount = int(call.data[11:])
    user_id = call.from_user.id
    place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()
    balance = cur.select("balance", "userdata").where(user_id=user_id).one()
    # treasury = cur.select("treasury", "globaldata").one()

    if place != "Живбанк":
        return

    if balance >= amount:
        cur.execute(f"UPDATE globaldata SET treasury=treasury+{amount}")
        conn.commit()
        cur.update("userdata").add(balance=-amount).where(
            user_id=user_id).commit()
        await call.answer('success.', show_alert=True)  # todo better answer
    else:
        await call.message.answer("&#10060; У вас недостаточно средств</i>")

    await state_balance(call)
    await bot.delete_message(call.message.chat.id, call.message.message_id)


async def economics(call: CallbackQuery) -> None:
    '''
    Callback for jivopolis economics menu

    :param call - callback:
    '''
    treasury = cur.execute("SELECT treasury FROM globaldata").fetchone()[0]
    try:
        balance = cur.execute(
            "SELECT clan_balance FROM clandata WHERE clan_id=-1001395868701"
        ).fetchone()[0]
    except TypeError:
        logger.warning(
            'Game club does not exists or bot not added to the chat'
        )
        balance = 0
    lastfill = cur.execute("SELECT lastfill FROM globaldata").fetchone()[0]
    coef = 1.5  # todo cur.execute("SELECT coef FROM globaldata").fetchone()[0]

    diff = time.time() - lastfill
    h = floor(diff / 3600)
    m = floor(diff % 3600 / 60)
    s = floor(diff % 3600 % 60)

    limits = ''

    for item in limited_items:
        limits += f'\n{ITEMS[item].emoji} {ITEMS[item].ru_name} - '
        item_left = cur.execute(f"SELECT {item} FROM globaldata").fetchone()[0]

        limits += 'дефицит' if item_left <= 0 else str(item_left)

    crypto = await get_crypto()
    crypto_text = ''
    for c in crypto:
        value = cur.select("value", 'cryptodata').where(crypto=c).one()
        prev_value = cur.select("prev_value", 'cryptodata').where(
            crypto=c).one()
        crypto_text += f"{ITEMS[c].emoji}{ITEMS[c].name} - ${value}"
        crypto_text += (
            f" 🔻 {round((value-prev_value) / prev_value * 100, 2)}%\n"
            if value-prev_value < 0 else
            f" 🔼 +{round((value-prev_value) / prev_value * 100, 2)}%\n"
        )
    await call.message.answer(
        (
            f"<i><b>📊 ЭКОНОМИКА ЖИВОПОЛИСА</b>\n"
            "\n💸 <b>Финансы</b>"
            f"\n💰 Государственная казна - <b>${treasury}</b>"
            f"\n🎮 Баланс Игрового клуба - <b>${balance}</b>"
            f"\n\n🏪 <b>Количество товара в Круглосуточном</b>{limits}\n"
            "\n\n🚚 Завоз товара в Круглосуточный осуществляется каждый день."
            f" Последний завоз был {h} часов {m} минут {s} секунд назад"
            "\n\n💰 <b>Центральный рынок</b>"
            f"\nРыночная ставка: {round(1//coef, 2)}</i>"
            "\n\n<b>💎 Криптовалюта:</b>\n\n"
            f"{crypto_text}"
        )
    )


async def toggle_nonick(call: CallbackQuery) -> None:
    if await is_allowed_nonick(call.from_user.id):
        new_mode = 0
        new_mode_ru = "выключен"
    else:
        new_mode = 1
        new_mode_ru = "включён"

    cur.update("userdata").set(nonick_cmds=new_mode).where(
        user_id=call.from_user.id).commit()

    await call.answer(f"👁 Nonick теперь {new_mode_ru}", show_alert=True)
    with contextlib.suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await call.message.delete()
    await user_settings(call)


async def user_settings(call: CallbackQuery):
    markup = InlineKeyboardMarkup(row_width=1)
    ready = cur.select("is_ready", "userdata").where(
        user_id=call.from_user.id).one()

    nonick = (
        "включён"
        if await is_allowed_nonick(call.from_user.id)
        else "выключен"
    )

    markup.add(
        InlineKeyboardButton(
            text=(
                f"⚔ Боевая готовность: "
                f"{'Готов' if bool(ready) else 'Не готов'}"
            ),
            callback_data='toggle_fightmode'
        ),
        InlineKeyboardButton(
            f"👁️‍🗨️ Nonick: {nonick}",
            callback_data="toggle_nonick"
        ),
        InlineKeyboardButton(
            text='👨‍🏫 Настройки профиля',
            callback_data='profile_settings'
        ),
        InlineKeyboardButton(
            text='🔐 Конфиденциальность',
            callback_data='privacy_settings'
        ),
        InlineKeyboardButton(
            text='◀ Назад',
            callback_data='cancel_action'
        )
    )
    await call.message.answer('<i><b>Настройки</b></i>', reply_markup=markup)


async def exchange_center(call: CallbackQuery) -> None:
    crypto = await get_crypto()
    buttons = [
        InlineKeyboardButton(
            f"{ITEMS[c].emoji} {ITEMS[c].ru_name}",
            callback_data=f"exchange_menu_{c}",
        )
        for c in crypto
    ]
    await call.message.answer(
        "📊 Добро пожаловать в нашу биржу! Выберите криптовалюту, "
        "которую вы бы хотели обменять.",
        reply_markup=InlineKeyboardMarkup(row_width=2).add(*buttons)
    )


async def exchange_menu_(call: CallbackQuery):
    crypto = call.data.replace("exchange_menu_", "")
    crypto_value = cur.select("value", from_="cryptodata").where(
        crypto=crypto).one()
    crypto = ITEMS[crypto]
    buttons = [
        InlineKeyboardButton(
            "📊 Купить ",
            callback_data=f"exchange_{crypto.name}:1"
        ),
        InlineKeyboardButton(
            "🔻 Продать ",
            callback_data=f"exchange_{crypto.name}:-1"
        )
    ]

    await call.message.answer(
        f"{crypto.emoji} {crypto.ru_name}\nТекущее значение: {crypto_value}",
        reply_markup=InlineKeyboardMarkup(row_width=1).add(*buttons)
    )


async def exchange_(call: CallbackQuery):
    amount = call.data.split("_")[1]
    crypto = amount.split(":")[0]
    amount = int(amount.split(":")[1])
    user_id = call.from_user.id
    balance = cur.select("balance", "userdata").where(user_id=user_id).one()

    cur.update("cryptodata")

    if amount > 0:
        cur.add(bought=amount)
        text = (
            f"🍏 Вы успешно приобрели {ITEMS[crypto].emoji}"
            f" {ITEMS[crypto].ru_name} в количестве {amount}. Ваш баланс: "
            f"{balance}"
        )
    else:
        cur.add(sold=amount)
        text = (
            f"🍎 Вы успешно продали {ITEMS[crypto].emoji} "
            f"{ITEMS[crypto].ru_name} в количестве {amount}."
            f"Ваш баланс: {balance}"
        )

    cur.where(crypto=crypto).commit()

    await call.answer(text, show_alert=True)
