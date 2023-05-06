import time
import contextlib
from math import floor
from ..callbacks.traveling import state_balance

from ... import bot, logger
from ...database import cur, conn
from ...database.functions import buybutton
from ...misc.config import limeteds
from ...misc import get_mask, get_link, OfficialChats, get_embedded_link, ITEMS

from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    Message, CallbackQuery
)
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound
from ..._world_updater import get_crypto
from ...utils import is_allowed_nonick

async def chats(user_id: int, message: Message) -> None:
    '''
    Callback for chats
    
    :param user_id:
    :param message:
    '''
    rase = cur.execute(f"SELECT rase FROM userdata WHERE user_id = {user_id}").fetchone()[0]
    markup = InlineKeyboardMarkup()

    match(rase):
        case "🐱":
            chat = "Расовый чат Котов"
            url = "https://t.me/joinchat/mWs48dy5cAo1ZmEy"
        case "🐶":
            chat = "Расовый чат Собак"
            url = "https://t.me/joinchat/yQ8X_uD1MydmNWIy"
        case "&#129437":
            chat = "Расовый чат Енотов"
            url = "https://t.me/joinchat/vuVCKuUIB2gxZTYy"
        case "&#128056;":
            chat = "Расовый чат Жаб"
            url = "https://t.me/joinchat/ACneINZ0hl43YTUy"
        case "&#129417;":
            chat = "Расовый чат Сов"
            url = "https://t.me/joinchat/nCt9oB_cX8I3NzMy"
        case _:
            chat = None

    if chat:
        markup.add(InlineKeyboardButton(text=chat, url=url))
    else:
        markup.add(InlineKeyboardButton(text="Выбрать расу", callback_data="change_rase"))
            
    markup.add(InlineKeyboardButton(text="🎮 Игровой клуб", url="https://t.me/+2UuPwVyac6lkYjRi"))
    
    await message.answer(
        "<i><b>Официальные чаты Живополиса</b>\n&#128221; Приёмная для идей и вопросов: https://t.me/zhivolab\n"
        "&#128172; Чат для общения: https://t.me/chatzhivopolisa\n&#128163; Чат для флуда: https://t.me/jivopoli"
        "s_flood\n&#128176; Рынок Живополиса: t.me/jivopolis_bazar\n&#128572; Посольство Живополиса в Котостане: "
        "https://t.me/posolstvo_jivopolis_in_kotostan\n{0}</i>"\
            .format("Вы ещё не выбрали себе расу. Чтобы выбрать, нажмите на кнопку \"Выбрать расу\"\n" if chat=="" else ""), reply_markup = markup)


async def my_refferals(message: Message, user_id: int) -> None:
    '''
    Callback for user refferals
    
    :param message:
    :param user_id:
    '''
    user_mask = get_mask(user_id)
    nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id = {user_id}").fetchone()[0]
    count = cur.execute(f"SELECT count(*) FROM userdata WHERE inviter_id = {user_id}").fetchone()[0]
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="🖇 Реферальная ссылка", callback_data="reflink"))

    if count < 1:
        return await message.answer(
            f"<i><b><a href=\"tg://user?id={user_id}\">{user_mask}{nick}</a></b>, вы пока никого не пригласили в Живополис :(</i>", 
            reply_markup=markup
        )

    cur.execute(f"""
    SELECT * FROM userdata 
    WHERE refid = {user_id}
    ORDER BY -lastseen 
    LIMIT 100""")

    users: str 

    for ref_num, row in enumerate(cur, start=1):
        mask = get_mask(row[1])
        users+=f"\n{ref_num}. <a href = \"{await get_link(row[1])}\">{mask}{row[7]}</a>"
    
    await message.answer(
        text=(
            f"<i>&#128100; Пользователи, привлечённые <b><a href=\"tg://user?id={user_id}\">{user_mask}{nick}</a></b>:"
            f" <b>{users}</b></i>"
        ),
        reply_markup=markup
    )


async def get_cheque(call: CallbackQuery, user_id: int) -> None:
    money = int(call.data[6:])
    mask = get_mask(user_id)
    nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id={user_id}").fetchone()[0]

    cur.execute(f"UPDATE userdata SET balance = balance + {money} WHERE user_id={user_id}")
    conn.commit()

    if call.message is None:
        await bot.edit_message_text(
            inline_message_id = call.inline_message_id, 
            text = f"<i><b><a href=\"{await get_link(user_id)}\">{mask}{nick}</a></b> забрал <b>${money}</b></i>")
    else:
        await bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = f"<i><b><a href=\"{await get_link(user_id)}\">{mask}{nick}</a></b> забрал <b>${money}</b></i>")
    if money > 0:
        await bot.send_message(OfficialChats.LOGCHAT, f"<i><b>{await get_embedded_link(user_id)}</b> забрал <b>${money}</b>\n#user_getcheck</i>")


async def cellphone_menu(call: CallbackQuery) -> None:
    '''
    Callback for cell phone menu
    
    :param call - callback:
    :param user_id:
    '''
    phone = cur.execute(f"SELECT phone FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]
    
    if phone<1:
        return await call.answer("Вам нужен телефон. Его можно купить в магазине на ул. Генерала Шелби и одноимённой станции метро", show_alert = True)
        
    markup = InlineKeyboardMarkup(row_width = 1)

    markup.add(InlineKeyboardButton(text="📡 GPS", callback_data="gps"),
    InlineKeyboardButton(text="🚚 МиГ.Доставка", callback_data="delivery_app"),
    InlineKeyboardButton(text="🚂 ЖивГорТранс: Билеты", callback_data="tickets"),
    InlineKeyboardMarkup(text="◀ Назад", callback_data="cancel_action"))

    await call.message.answer("<i>📱 Телефон - это удобная и современная вещь</i>", reply_markup = markup)


async def give_state(call: CallbackQuery, amount) -> None:
    '''
    Callback for clan joining
    
    :param call - callback:
    :param user_id:
    '''
    amount = int(call.data[11:])
    user_id = call.from_user.id
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={user_id}").fetchone()[0]
    balance = cur.execute(f"SELECT balance FROM userdata WHERE user_id={user_id}").fetchone()[0]
    treasury = cur.execute("SELECT treasury FROM globaldata").fetchone()[0]

    if place != "Живбанк":
        return

    if balance>=amount:
        cur.execute(f"UPDATE globaldata SET treasury=treasury+{amount}"); conn.commit()
        cur.execute(f"UPDATE userdata SET balance=balance-{amount} WHERE user_id={user_id}"); conn.commit()
        await call.answer('success.', show_alert=True) #todo better answer
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
        logger.warning('Game club does not exists or bot not added to the chat')
        balance = 0
    lastfill = cur.execute("SELECT lastfill FROM globaldata").fetchone()[0]
    coef = 1.5 #todo cur.execute("SELECT coef FROM globaldata").fetchone()[0]

    diff = time.time() - lastfill
    h = floor(diff/3600)
    m = floor(diff%3600/60)
    s = floor(diff%3600%60)

    limits = ''

    for item in limeteds:
        limits += f'\n{ITEMS[item].emoji} {ITEMS[item].ru_name} - '
        item_left = cur.execute(f"SELECT {item} FROM globaldata").fetchone()[0]

        limits += 'дефицит' if item_left <= 0 else str(item_left)
    
    crypto = await get_crypto()
    crypto_text = ''
    for c in crypto:
        value = cur.execute(f"SELECT value FROM cryptodata WHERE crypto='{c}'").fetchone()[0]
        prev_value = cur.execute(f"SELECT prev_value FROM cryptodata WHERE crypto=\"{c}\"").fetchone()[0]
        crypto_text += f"{ITEMS[c].emoji}{ITEMS[c].name} - ${value}"
        crypto_text += f" 🔻 {round((value-prev_value)/prev_value*100, 2)}%\n" if value-prev_value < 0 else f" 🔼 +{round((value-prev_value)/prev_value*100, 2)}%\n"
    return await call.message.answer(
        (
            f"<i><b>📊 ЭКОНОМИКА ЖИВОПОЛИСА</b>\n"
            "\n💸 <b>Финансы</b>"
            f"\n💰 Государственная казна - <b>${treasury}</b>"
            f"\n🎮 Баланс Игрового клуба - <b>${balance}</b>"
            f"\n\n🏪 <b>Количество товара в Круглосуточном</b>{limits}\n"
            f"\n\n🚚 Завоз товара в Круглосуточный осуществляется каждый день. Последний завоз был {h} часов {m} минут {s} секунд назад"
            "\n\n💰 <b>Центральный рынок</b>"
            f"\nРыночная ставка: {round(1//coef, 2)}</i>"
            "\n\n<b>💎 Криптовалюта:</b>\n\n"
            f"{crypto_text}"
        )
    )
            

async def toggle_nonick(call: CallbackQuery) -> None:
    if await is_allowed_nonick(call.from_user.id):
        cur.execute(f"UPDATE userdata SET nonick_cmds=0 WHERE user_id={call.from_user.id}")
        change = "выключен"
    else:
        cur.execute(f"UPDATE userdata SET nonick_cmds=1 WHERE user_id={call.from_user.id}")
        change = "включён"

    await call.answer(f"👁 Nonick теперь {change}", show_alert=True)
    with contextlib.suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await call.message.delete()
    await user_settings(call)

async def user_settings(call: CallbackQuery):
    markup = InlineKeyboardMarkup(row_width=1)
    ready = cur.execute(
                f'SELECT is_ready FROM userdata WHERE user_id={call.from_user.id}'
            ).fetchone()[0]
    if await is_allowed_nonick(call.from_user.id):
        nonick = "включён"
    else:
        nonick = "выключен"
    markup.add(
        InlineKeyboardButton(text=f"⚔ Боевая готовность: {'Готов' if bool(ready) else 'Не готов'}", callback_data='toggle_fightmode'),
        InlineKeyboardButton(f"👁️‍🗨️ Nonick: {nonick}", callback_data="toggle_nonick"),
        InlineKeyboardButton(text='👨‍🏫 Настройки профиля', callback_data='profile_settings'),
        InlineKeyboardButton(text='🔐 Конфиденциальность', callback_data='privacy_settings')
    )
    await call.message.answer('<i><b>Настройки</b></i>' , reply_markup = markup)


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
        "📊 Добро пожаловать в нашу биржу! Выберите криптовалюту, которую вы бы хотели обменять.", 
        reply_markup=InlineKeyboardMarkup(row_width=2).\
            add(buttons)
    )

async def exchange_menu_(call: CallbackQuery):
    crypto = call.data.replace("exchange_menu_", "")
    crypto_value = cur.select("value", _from="cryptodata").where(crypto=crypto).one()
    crypto = ITEMS[crypto]
    buttons = [
        InlineKeyboardButton("📊 Купить ", callback_data=f"exchange_{crypto}:1"),
        InlineKeyboardButton("🔻 Продать ", callback_data=f"exchange_{crypto}:-1")
    ]
    await call.message.answer(
        f"{crypto.emoji} {crypto.ru_name}\nТекущее значение: {crypto_value}",
        reply_markup=InlineKeyboardMarkup().add(buttons)
    )


async def exchange_(call: CallbackQuery):
    value = call.data.split("_")[1]
    crypto = value.split(":")[0]
    value = value.split(":")[1]

    cur.update("cryptodata")
    if value > 0:
        cur.add(bought=value)
        
    else:
        cur.add(sold=value)
    cur.where(crypto=crypto).commit()