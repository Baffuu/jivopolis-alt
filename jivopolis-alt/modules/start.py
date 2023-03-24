import random
import sqlite3

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.deep_linking import decode_payload

from ..config import levelrange, hellos, randomtext, log_chat, SUPPORT_LINK

from .. import bot, Dispatcher, logger

from ..database.sqlitedb import cur, conn
from ..database.functions import check, create_acc, profile

from ..misc import get_mask, get_link

async def start_cmd(message: Message):
    try:
        user_id = message.from_user.id            
        chat_id = message.chat.id
        markup = InlineKeyboardMarkup(row_width=2)
        
        if message.chat.type == "private":
            try:
                nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id = {user_id}").fetchone()[0]
                health = cur.execute(f"SELECT health FROM userdata WHERE user_id = {user_id}").fetchone()[0]
                is_banned = bool(cur.execute(f"SELECT is_banned FROM userdata WHERE user_id = {message.from_user.id}").fetchone()[0])
                
                await check(user_id, chat_id)

                if is_banned:
                    return await bot.send_message(message.from_user.id, f'🧛🏻‍♂️ Вы были забаненны в боте. Если вы считаете, что это - ошибка, обратитесь в <a href="{SUPPORT_LINK}">поддержку</a>.')

                if health < 0:
                    return await message.reply("<i>&#9760; Вы умерли. Попросите кого-нибудь вас воскресить</i>", parse_mode = "html")         
            except TypeError:
                markup.add(InlineKeyboardButton(text="Создать аккаунт", callback_data="sign_up"))
                markup.add(InlineKeyboardButton(text="Войти", callback_data="log_in"))
                
                reflink = message.get_args()
                
                if reflink == '':
                    return await bot.send_message(user_id, f"<i>&#128075; <b>{message.from_user.full_name}, привет!</b>\
                    \nТы попал в <code>Живополис</code>.\
                    \nЭто лучший игровой бот в Telegram\
                    \n\
                    \nУдачной игры!</i>", reply_markup=markup)
                else:
                    try:
                        inviter: int = cur.execute(f"SELECT COUNT(*) FROM userdata WHERE login_id = \"{reflink}\"").fetchone()[0]
                    except TypeError:
                        inviter = 0
                    
                    if inviter == 1:
                        await create_acc(message.from_user, message.from_user.id)
                        
                        cur.execute(f"UPDATE userdata SET inviter_id={decode_payload(reflink)} WHERE user_id={user_id}"); conn.commit()
                        cur.execute(f"UPDATE userdata SET balance = balance + 100 WHERE login_id='{reflink}'"); conn.commit()
                        cur.execute(f"UPDATE userdata SET balance = balance + 100 WHERE user_id='{user_id}'"); conn.commit()
                        
                    elif inviter == 0:
                        return await bot.send_message(user_id, f"<i>&#128075; <b>{message.from_user.full_name}, привет!</b>\
                        \nТы попал в <code>Живополис</code>.\
                        \nЭто лучший игровой бот в Telegram\
                        \n\
                        \nУдачной игры!</i>", reply_markup=markup)
                return
            
            leaders = "&#127942; Лидеры Живополиса на данный момент:"

            args = message.get_args()

            if args != '':
                try:
                    usercount = cur.execute(f"SELECT COUNT(*) FROM userdata WHERE user_id={args}").fetchone()[0]
                except sqlite3.OperationalError:
                    usercount = 0
                if usercount == 0:
                    pass
                elif usercount == 1:
                    logger.debug('true')
                    return await profile(args, message)

            cur.execute("""
            SELECT * FROM userdata 
            WHERE profile_type=\"public\" AND rank=0 
            ORDER BY balance 
            DESC LIMIT 10""")

            for row in cur:
                leaders += f"\n<b><a href=\"{get_link(row[1])}\">{get_mask(row[1])}{row[2]}</a> - ${row[4]}</b>"
            
            mask = get_mask(user_id)
            rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id = {user_id}").fetchone()[0]
            phone = cur.execute(f"SELECT phone FROM userdata WHERE user_id = {user_id}").fetchone()[0]
            
            buttons = [InlineKeyboardButton(text="💼 Инвентарь", callback_data="inventory"), 
                       InlineKeyboardButton(text="🏛 Город", callback_data="city"),
                       InlineKeyboardButton(text="📬 Почтовый ящик", callback_data="mailbox"), 
                       InlineKeyboardButton(text="💬 Чаты", callback_data="chats"),
                       InlineKeyboardButton(text="🤵 Работать", callback_data="work"),
                       InlineKeyboardButton(text="🃏 Профиль", callback_data="profile"),
                       InlineKeyboardButton(text="⚙ Настройки", callback_data="user_settings"),
                       InlineKeyboardButton(text="📊 Экономика", callback_data="economics"),
                       InlineKeyboardButton(text="❓ Помощь", callback_data="help")]

            if phone > 0:
                buttons.append(InlineKeyboardButton(text="📱 Телефон", callback_data="cellphone_menu"))

            if rank >= 2:
                markup.add(InlineKeyboardButton(text="👑 Админская панель", callback_data="adminpanel"))

            markup.add(*buttons)
            balance = cur.execute(f"SELECT balance FROM userdata WHERE user_id = {user_id}").fetchone()[0]
            xp = cur.execute(f"SELECT xp FROM userdata WHERE user_id = {user_id}").fetchone()[0]
            health = cur.execute(f"SELECT health FROM userdata WHERE user_id = {user_id}").fetchone()[0]
            level = cur.execute(f"SELECT level FROM userdata WHERE user_id={user_id}").fetchone()[0]

            if level <= len(levelrange):
                xp_left = f"XP из {levelrange[level+1]}"
            else:
                xp_left = "макс. уровень"

            hello = random.choice(hellos)
            text = f"<i>{hello}, <b><a href=\"tg://user?id={user_id}\">{mask}{nick}</a></b>\
                \n💲 Баланс: <b>${balance}</b>\
                \n 💡 Уровень: <b>{level}</b> ({xp} {xp_left})\
                \n❤️ Здоровье: <b>{health}</b>\
                \n{leaders}</i>"
            
            await message.answer(f"<i>{random.choice(randomtext)}</i>", parse_mode="html")
            return await message.answer(text, parse_mode="html", reply_markup=markup)

        else: #todo
            user_id = message.from_user.id
            chat_id = message.chat.id

            count = cur.execute(f"SELECT count(*) FROM clandata WHERE clan_id = {chat_id}").fetchone()[0]
            
            if count == 0:
                markup.add(InlineKeyboardButton(text="➕ Создать", callback_data="create_clan"))
                return await bot.send_message(chat_id, f"<i>Создать клан <b>{message.chat.title}</b></i>", reply_markup = markup)
            else:

                description = cur.execute(f"SELECT description FROM clandata WHERE clan_id={chat_id}").fetchone()[0]

                markup.add(InlineKeyboardButton(text="➕ Вступить/Выйти", callback_data="join_clan"),
                    InlineKeyboardButton(text="👥 Участники клана", callback_data="clan_members"),
                    InlineKeyboardButton(text="✏ Управление", callback_data="clan_settings"),
                    InlineKeyboardButton(text="📣 Созвать клан", callback_data="call_clan"),
                    InlineKeyboardButton(text="🏗 Комнаты (постройки)", callback_data="clan_buildings"))
                
                clan_name = cur.execute(f"SELECT clan_name FROM clandata WHERE clan_id = {chat_id}").fetchone()[0]
                clan_balance = None #cur.execute(f"SELECT balance FROM clandata WHERE clan_id = {chat_id}").fetchone()[0]
                HQplace = None #cur.execute(f"SELECT hqplace FROM clandata WHERE clan_id = {chat_id}").fetchone()[0]
                address = None #cur.execute(f"SELECT address FROM clandata WHERE clan_id = {chat_id}").fetchone()[0]
                clanphoto = cur.execute(f"SELECT photo_id FROM clandata WHERE clan_id = {chat_id}").fetchone()[0]

                leaders = "&#127942; Топ кланов на данный момент:"
                
                '''count = cur.execute("SELECT COUNT(*) FROM clandata WHERE (type=? AND balance < 1000000) OR clan_id=-1001395868701", ("public",)).fetchone()[0]
                
                cur.execute("""SELECT * FROM clandata
                WHERE (type=? AND balance < 1000000) OR clan_id=-1001395868701
                ORDER BY balance DESC
                LIMIT 10""", ("public",))

                for row in cur:
                    leaders += f"\n<b><a href=\"{row[8]}\">{row[1]}</a> - ${row[4]}</b>"'''

                description = ("\n" + description + '\n\n') if description else ""
                hqplace = (f"{HQplace}, {address}") if HQplace else "отсутствует"

                text = f"<i>Клан <b>{clan_name}</b>\
                    \n{description}&#128176; Баланс: <b>${clan_balance}</b>\
                    \n&#127970; Штаб-квартира: <b>{hqplace}</b>\
                    \n{leaders if count != 0 else ''}</i>"
                
                if not clanphoto:
                    return await bot.send_message(chat_id, text, reply_markup = markup)
                else:
                    try:
                        return await bot.send_photo(chat_id, clanphoto, caption=text, reply_markup = markup)
                    except:
                        return await bot.send_message(chat_id, text, reply_markup = markup)
        
        return await bot.send_message(message.chat.id, text)
    except Exception as e:
        logger.exception(e)
        return await bot.send_message(chat_id, f"<i><b>&#10060; Ошибка: </b>{e}</i>")

def register(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=['start'])