import random
import sqlite3
import contextlib

from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, User, ChatType, Chat
from aiogram.utils.exceptions import ChatNotFound, BotBlocked, CantInitiateConversation
from aiogram.utils.deep_linking import decode_payload

from .. import bot, Dispatcher, logger
from ..misc import get_mask, get_link, current_time, OfficialChats, constants
from ..database.sqlitedb import cur, conn, insert_user
from ..database.functions import check, profile
from ..misc.config import levelrange, hellos, randomtext, SUPPORT_LINK

class StartCommand():

    async def start_cmd(self, message: Message) -> None:
        '''
        handler for start command 

        :param message:
        '''
        try:
            user_id = message.from_user.id
            chat_id = message.chat.id

            usercount = cur.execute(f"SELECT count(*) FROM userdata WHERE user_id = {user_id}").fetchone()[0]
            if usercount < 1:
                return await self._user_register_message(message, user_id)

            await check(user_id, chat_id)

            if args := message.get_args():
                usercount = cur.execute(f"SELECT COUNT(*) FROM userdata WHERE user_id={args}").fetchone()[0]
                if usercount == 0:
                    pass
                elif usercount == 1:
                    return await profile(args, message)

            is_banned = bool(cur.execute(f"SELECT is_banned FROM userdata WHERE user_id = {message.from_user.id}").fetchone()[0])
            if is_banned:
                return await message.answer(
                    f'🧛🏻‍♂️ Вы были забаненны в боте. Если вы считаете, что это - ошибка, обратитесь в <a href="{SUPPORT_LINK}">поддержку</a>.'
                )

            health = cur.execute(f"SELECT health FROM userdata WHERE user_id = {user_id}").fetchone()[0]
            if health < constants.MINIMUM_HEALTH:
                return await message.reply("<i> Вы умерли. Попросите кого-нибудь вас воскресить</i>")                

            if message.chat.type == ChatType.PRIVATE:
                await self._private_start(user_id)
            elif message.chat.id == OfficialChats.CASINOCHAT:
                await self._casino_start(message)
            elif message.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
                await self._clan_start(message.chat)
        except Exception as e:
            logger.exception(e)
            return await bot.send_message(chat_id, constants.ERROR_MESSAGE.format(e))
    
    
    async def _private_start(self, user_id: str) -> None:
        nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id = {user_id}").fetchone()[0]


        cur.execute("""
            SELECT * FROM userdata 
            WHERE profile_type=\"public\" AND rank=0 
            ORDER BY balance 
            DESC LIMIT 10
        """)

        leaders = "&#127942; Лидеры Живополиса на данный момент:"

        for row in cur:
            leaders += f"\n<b><a href=\"{await get_link(row[1])}\">{get_mask(row[1])}{row[2]}</a> - ${row[4]}</b>"

        buttons = self._start_buttons(user_id)
        mask = get_mask(user_id)

        balance = cur.execute(f"SELECT balance FROM userdata WHERE user_id = {user_id}").fetchone()[0]
        xp = cur.execute(f"SELECT xp FROM userdata WHERE user_id = {user_id}").fetchone()[0]
        health = cur.execute(f"SELECT health FROM userdata WHERE user_id = {user_id}").fetchone()[0]
        level = cur.execute(f"SELECT level FROM userdata WHERE user_id={user_id}").fetchone()[0]

        if level <= len(levelrange):
            xp_left = f"{xp} XP из {levelrange[level+1]}"
        else:
            xp_left = "макс. уровень"

        hello = random.choice(hellos)
        text = (
            f"<i>{hello}, <b><a href=\"tg://user?id={user_id}\">{mask}{nick}</a></b>"
            f"\n💲 Баланс: <b>${balance}</b>"
            f"\n 💡 Уровень: <b>{level}</b> ({xp_left})"
            f"\n❤️ Здоровье: <b>{health}</b>"
            f"\n{leaders}</i>"
        )

        await bot.send_message(user_id, f"<i>{random.choice(randomtext)}</i>")
        await bot.send_message(
            user_id, 
            text, 
            reply_markup=InlineKeyboardMarkup(row_width=2).add(*buttons)
        )


    def _start_buttons(self, user_id) -> list[InlineKeyboardButton]:
        rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id = {user_id}").fetchone()[0]
        phone = cur.execute(f"SELECT phone FROM userdata WHERE user_id = {user_id}").fetchone()[0]

        buttons = [
                InlineKeyboardButton(text="💼 Инвентарь", callback_data="inventory"), 
                InlineKeyboardButton(text="🏛 Город", callback_data="city"),
                InlineKeyboardButton(text="📬 Почтовый ящик", callback_data="mailbox"), 
                InlineKeyboardButton(text="💬 Чаты", callback_data="chats"),
                InlineKeyboardButton(text="🤵 Работать", callback_data="work"),
                InlineKeyboardButton(text="🃏 Профиль", callback_data="profile"),
                InlineKeyboardButton(text="⚙ Настройки", callback_data="user_settings"),
                InlineKeyboardButton(text="📊 Экономика", callback_data="economics"),
                InlineKeyboardButton(text="❓ Помощь", callback_data="help")
            ]

        if phone > 0:
            buttons.append(InlineKeyboardButton(text="📱 Телефон", callback_data="cellphone_menu"))

        if rank >= constants.ADMINPANEL_MINIMUM_RANK:
            buttons.append(InlineKeyboardButton(text="👑 Админская панель", callback_data="adminpanel"))

        return buttons


    async def sign_up_refferal(
        self,
        message: Message, 
        user: User, 
        refferal_id: int
    ):
        '''
        Creates account for a user that sign up using refferal code 

        :param message:
        :param user:
        :param refferal_id:
        '''
        if cur.execute(
            f"SELECT count(*) FROM userdata WHERE user_id = {user.id}"
        ).fetchone():
            insert_user(user)
        else:
            return message.answer("<i>😨 Вы уже создавали аккаунт</i>", reply_markup = ReplyKeyboardRemove())
        refferal_nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id=\"{refferal_id}\"").fetchone()[0]
        refferal_mask = get_mask(refferal_id)

        await message.edit_text(
            f"{message.text}\n\n>>> 🤵‍♂️Вы были приглашены пользователем <a href='{await get_link(refferal_id)}'>{refferal_mask}{refferal_nick}</a>",
        )

        cur.execute(f"UPDATE userdata SET inviter_id={refferal_id} WHERE user_id={user.id}")
        conn.commit()

        cur.execute(f"UPDATE userdata SET lootbox = lootbox + 1 WHERE user_id='{refferal_id}'")
        conn.commit()

        cur.execute(f"UPDATE userdata SET balance = balance + 100 WHERE user_id='{user.id}'")
        conn.commit()

        with contextlib.suppress(ChatNotFound, BotBlocked, CantInitiateConversation):
            await bot.send_message(
                refferal_id,
                (
                    f"👼 Юзер <a href = '{await get_link(user.id)}'>{user.full_name}</a> зарегистрировался по вашей реферальной ссылке, "
                    "спасибо за приглашение новых участников в игру!\n\n"
                    ">>> 🤵‍♂️Получен <b>📦 Лутбокс</b>"
                ),
            )

        await message.answer("<i>👾 Вы успешно зарегистрировались в живополисе! Добро пожаловать :3</i>", reply_markup = ReplyKeyboardRemove())
        await self._private_start(user.id)


    async def _register_refferal(self, message: Message, ref_id: int):
        '''
        Send message for refferal registration 

        :param message:
        :param red_id - refferal user ID:
        '''

        await message.answer(
            (
                f"🦎 Привет, {message.from_user.full_name}! Добро пожаловать в Живополис, лучший игровой бот во всея телеграмме! "
                "\n\n⚙️ Нажмите на кнопку ниже для того, чтобы создать аккаунт и начать играть…"
            ),
            reply_markup=InlineKeyboardMarkup(row_width=1).\
                add(
                    InlineKeyboardButton("👼 Создать аккаунт", callback_data=f'sign_up_{ref_id}')
                )
        )


    async def _user_register_message(self, message: Message, user_id: int):
        '''
        Preparing user for signing up

        :param message: 
        :param user_id:
        '''
        markup = InlineKeyboardMarkup(row_width=1).\
            add(
                InlineKeyboardButton(
                    text="👼 Создать аккаунт",
                    callback_data="sign_up"
                ),
                InlineKeyboardButton(
                    text="🔮 Войти в существующий",
                    callback_data="log_in"
                )
            )

        refferal_link = message.get_args()

        if not refferal_link:
            await bot.send_message(
                user_id, 
                text=(   
                    f"🦎 Привет, {message.from_user.full_name}! Добро пожаловать в Живополис, лучший игровой бот во всея телеграмме! "
                    "\n\n⚙️ Нажмите на кнопку ниже для того, чтобы создать аккаунт и начать играть…"
                ),
                reply_markup=markup
            )
            return 


        try:
            inviter = cur.execute(f"SELECT COUNT(*) FROM userdata WHERE login_id = \"{refferal_link}\"").fetchone()[0]
        except TypeError:
            inviter = 0


        if inviter < 1:
            await bot.send_message(
                user_id, 
                text=(   
                    f"🦎 Привет, {message.from_user.full_name}! Добро пожаловать в Живополис, лучший игровой бот во всея телеграмме! "
                    "\n\n⚙️ Нажмите на кнопку ниже для того, чтобы создать аккаунт и начать играть…"
                ),
                reply_markup=markup
            )
        elif inviter > 1:
            raise ValueError("more than one inviter with this referal ID")
        elif inviter == 1:
            await self._register_refferal(message, decode_payload(refferal_link))


    async def _clan_start(self, chat: Chat):
        '''
        start command in clan 

        :param chat:
        '''
        count = cur.execute(f"SELECT count(*) FROM clandata WHERE clan_id = {chat.id}").fetchone()[0]

        if count == 0:
            return await bot.send_message(chat.id,
                f"<i>Создать клан <b>{chat.title}</b></i>", 
                reply_markup = InlineKeyboardMarkup().add(
                    InlineKeyboardButton(text="➕ Создать", callback_data="create_clan")
                )
            )

        description = cur.execute(f"SELECT description FROM clandata WHERE clan_id={chat.id}").fetchone()[0]

        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton('🤵‍♂️ Присоединяться', callback_data="join_clan"),
            InlineKeyboardButton("🥾 Покинуть", callback_data="leave_clan")
        ).add(
            InlineKeyboardButton("🏗 Постройки", callback_data="clan_buildings"),
            InlineKeyboardButton("👥 Участники", callback_data="clan_members")
        ).add(
            InlineKeyboardButton("🔝", callback_data="clan_top"),
            InlineKeyboardButton("⚙️", callback_data="clan_settings"),
            InlineKeyboardButton("📣", callback_data="call_clan")
        )

        clan_name = cur.execute(f"SELECT clan_name FROM clandata WHERE clan_id = {chat.id}").fetchone()[0]
        clan_balance = cur.execute(f"SELECT clan_balance FROM clandata WHERE clan_id = {chat.id}").fetchone()[0]
        top = cur.execute("SELECT clan_id FROM clandata ORDER BY clan_balance").fetchall()

        top_num = 0
        for i in top:
            top_num += 1
            if i == chat.id:
                break

        HQplace = cur.execute(f"SELECT HQ_place FROM clandata WHERE clan_id = {chat.id}").fetchone()[0]
        address = cur.execute(f"SELECT address FROM clandata WHERE clan_id = {chat.id}").fetchone()[0]
        clanphoto = cur.execute(f"SELECT photo_id FROM clandata WHERE clan_id = {chat.id}").fetchone()[0]

        members_count = cur.execute(f"SELECT count(*) FROM userdata WHERE clan_id={chat.id}").fetchone()[0]

        text = f"""
            🏯 Клан {clan_name}{description or ''}
            \n\n🏬 Штаб-квартира: {HQplace} {f', {address}' if address else ''}
            \n\n{members_count} 👥 {clan_balance} 💲{top_num} 🔝
        """

        return (
            await bot.send_photo(
                chat.id, clanphoto, caption=text, reply_markup=markup
            )
            if clanphoto
            else await bot.send_message(chat.id, text, reply_markup=markup)
        )


    async def _casino_start(self, message: Message):
        balance = cur.execute(
            f"SELECT clan_balance FROM clandata WHERE clan_id = {OfficialChats.CASINOCHAT}"
        ).fetchone()[0]
        treasury = cur.execute(
            "SELECT treasury FROM globaldata"
        ).fetchone()[0]

        await message.answer(
            (
                "🎮 Добро пожаловать в игровой клуб! Здесь вы можете повеселиться и попробовать"
                " заработать немного денег. Но будьте осторожны, иначе казино заберёт у вас последние гроши…"
                "\n\n‼️ Мы крайне не рекомендуем играть в казино в реальной жизни, особенно на большие деньги."
                f"\n\n💲Баланс Казино: {balance}"
                f"\n\n🏦 Казна Живополиса: {treasury}"
            ),
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(
                    text="❓Помощь по мини-играм",
                    callback_data="casino_help"
                )
            )
        )


async def create_acc(user: User, chat_id: int) -> None:
    '''
    Shell for inserting user into database 

    :param user (aiogram.types.User) - user that will be inserted
    :param chat_id (int) - chat id in which messages will be sent 
    ''' 
    try: 
        count = cur.execute(f"SELECT COUNT(*) FROM userdata WHERE user_id={user.id}").fetchone()[0]

        if count > 0:
            return await bot.send_message(chat_id, "<i>😨 Вы уже создавали аккаунт</i>", reply_markup = ReplyKeyboardRemove())
            
        insert_user(user)
        await bot.send_message(
            OfficialChats.LOGCHAT, 
            f"<i><b><a href=\"{await get_link(user.id)}\">{user.full_name}</a></b> присоединился(-ась) к Живополису\n#user_signup</i>"
        )
        
        cur.execute(f"UPDATE userdata SET register_date = {current_time()} WHERE user_id={user.id}")
        conn.commit()

    except Exception as e:
        if str(e).startswith("UNIQUE constraint failed: "):
            logger.exception(e)
            await bot.send_message(chat_id, "<i>😨 Вы уже создавали аккаунт</i>", reply_markup = ReplyKeyboardRemove())
        else:
            logger.exception(e)
        return
    
    return await bot.send_message(chat_id, "<i>👾 Вы успешно зарегистрировались в живополисе! Добро пожаловать :3</i>", reply_markup = ReplyKeyboardRemove())


def register(dp: Dispatcher):
    dp.register_message_handler(StartCommand().start_cmd, commands=['start'])