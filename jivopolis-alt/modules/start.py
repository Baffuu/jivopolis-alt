from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ..database.sqlitedb import check, cur

async def start_cmd(message: Message):
    try:
        user_id = message.from_user.id
        
        await check(user_id, message.chat.id)
        cur.execute('select health from userdata where user_id=?', (message.from_user.id,)).fetchone()
        health = cur.fetchone()[0]
        if health <= 0:
            await message.reply('<i>&#9760; Вы умерли. Попросите кого-нибудь вас воскресить</i>', parse_mode = 'html')
            return
    except Exception as e:
        print(e)
    try:
        chat_id = message.chat.id
        if message.chat.type == "private":
            err = ''
            unerrored = True
            leader = '&#127942; Лидеры Живополиса на данный момент:'
            try:
                rasa = cur.execute(f'SELECT rasa FROM userdata WHERE user_id = {user_id}').fetchone()
                nick = cur.execute(f'SELECT nick FROM userdata WHERE user_id = {user_id}').fetchone()
            except:
                markup = InlineKeyboardMarkup()
                button = InlineKeyboardButton(text='Создать аккаунт', callback_data='{0}'.format(createacc2))
                markup.add(button)
                button = InlineKeyboardButton(text='Войти', callback_data='log_in')
                markup.add(button)
                text = f"<i>&#128075; <b>{message.from_user.full_name}, привет!</b>\nТы попал в <code>Живополис</code>.\
                Это лучший игровой бот в Telegram\n\nУдачной игры!</i>"
            else:
                cur.execute('''SELECT * FROM userdata WHERE type="public" AND rang=0 ORDER BY balance DESC LIMIT 10''')
                for row in cur:
                    leader+=f'\n<b><a href="tg://user?id={row[1]}">{row[9]}{row[7]}</a> - ${3}</b>'.format(row[1], row[9], row[7], row[5])
                rank = cur.execute(f'SELECT rank FROM userdata WHERE user_id = {user_id}').fetchone()
                phone = cur.execute(f'SELECT phone FROM userdata WHERE user_id = {user_id}').fetchone()

                markup = InlineKeyboardMarkup(row_width=2)
                buttons = [InlineKeyboardButton(text='💼 Инвентарь', callback_data='inventory'),
                    InlineKeyboardButton(text='🏛 Город', callback_data='city'),
                    InlineKeyboardButton(text='📬 Почтовый ящик', callback_data='mailbox'), 
                    InlineKeyboardButton(text='💬 Чаты', callback_data='chats'),
                    InlineKeyboardButton(text='🤵 Работать', callback_data='work'),
                    InlineKeyboardButton(text='🃏 Профиль', callback_data='profile'),
                    InlineKeyboardButton(text='⚙ Настройки', callback_data='user_settings'),
                    InlineKeyboardButton(text='📊 Экономика', callback_data='economics'),
                    InlineKeyboardButton(text='❓ Помощь', callback_data='help')]

                if phone >= 1:
                    buttons.append(InlineKeyboardButton(text='📱 Телефон', callback_data='smartphone'))

                buttons.append(**[])

                if rank >= 2:
                    buttons.append(InlineKeyboardButton(text='👑 Админская панель', callback_data='adminpanel'))

                markup.add(**buttons)
                balance = cur.execute(f'SELECT balance FROM userdata WHERE user_id = {user_id}')
                points = cur.execute(f'SELECT points FROM userdata WHERE user_id = {user_id}')
                health = cur.execute(f'SELECT health FROM userdata WHERE user_id = {user_id}')
                health = cursor.fetchone()[0]
                cursor.execute('SELECT lvl FROM userdata WHERE user_id=?', (a,))
                lvl = cursor.fetchone()[0]
                if lvl<len(levelrange)-1:
                    rem = 'из {0}'.format(levelrange[lvl+1])
                else:
                    rem = '- макс. уровень'
                rand = random.choice(hellos)
                text = '<i>{6}, <b><a href="tg://user?id={2}">{0}{1}</a></b>\n&#128178; Баланс: <b>${4}</b>\n&#128305; Уровень: {5}\n&#128138; Здоровье: <b>{7}</b>\n{3}</i>'.format(ras,nick, a, leader, balance, '<b>{0}</b> ({1} {2})'.format(lvl, points, rem), rand, health)
                await message.answer('<i>{0}</i>'.format(random.choice(randomtext)), parse_mode='html')
                await message.answer(text, parse_mode='html', reply_markup=markup)
                if " " in message.text:
                    reflink = message.text.split()[1]
                else:
                    return
            cursor.execute('SELECT count(user_id) FROM userdata WHERE ref=?', (reflink,))
            count = cursor.fetchone()[0]
            if count!=1:
                unerrored = False
                err += '\n•Неверная реферальная ссылка'
                referrer_candidate = 0
            else:
                cursor.execute('SELECT user_id FROM userdata WHERE ref=?', (reflink,))
                referrer_candidate = cursor.fetchone()[0]
            try:
                cursor.execute('SELECT balance FROM userdata WHERE user_id = ?', (referrer_candidate,))
                temp = cursor.fetchone()[0]
                cursor.execute('UPDATE userdata SET balance = ? WHERE user_id = ?', (temp, referrer_candidate,))
                conn.commit()
            except Exception as e:
                unerrored = False
                err += '\n•Пользователя, по чьей реферальной ссылке вы перешли, нет в Живополисе\n•<b>Исключение:</b> {0}'.format(e)
            if a==referrer_candidate:
                unerrored = False
                err += '\n•Вы перешли по собственной реферальной ссылке'
            try:
                cursor.execute('SELECT count(id) FROM userdata WHERE user_id=?', (a,))
                count = cursor.fetchone()[0]
                if count>0:
                    unerrored = False
                    err += '\n•У вас уже был аккаунт до перехода по ссылке'
            except:
                pass
            if unerrored:
                try:
                    await create_acc(message.from_user, message.chat.id)
                    cursor.execute('SELECT place FROM userdata WHERE user_id = ?', (referrer_candidate,))
                    st = cursor.fetchone()[0]
                    cursor.execute('UPDATE userdata SET balance=balance+100 WHERE user_id=?', (message.from_user.id,))
                    conn.commit()
                    cursor.execute('UPDATE userdata SET place=? WHERE user_id=?', (st, message.from_user.id,))
                    conn.commit()
                    cursor.execute('UPDATE userdata SET refid=? WHERE user_id=?', (referrer_candidate, message.from_user.id,))
                    conn.commit()
                    await message.answer('<i>&#9989; Вам зачислено $100 на баланс</i>', parse_mode = 'html');
                except Exception as e:
                    unerrored = False
                    err += '\n•У вас уже был аккаунт до перехода по ссылке\n•<b>Исключение:</b> {0}'.format(e)
            if unerrored:
                cursor.execute('SELECT nick FROM userdata WHERE user_id = ?', (referrer_candidate,))
                onick = cursor.fetchone()[0]
                cursor.execute('SELECT rasa FROM userdata WHERE user_id = ?', (referrer_candidate,))
                orasa = cursor.fetchone()[0]
                cursor.execute('SELECT nick FROM userdata WHERE user_id = ?', (a,))
                nick = cursor.fetchone()[0]
                cursor.execute('SELECT rasa FROM userdata WHERE user_id = ?', (a,))
                rasa = cursor.fetchone()[0]
                await main.send_message(fid, '<i><b><a href="tg://user?id={2}">{1}{0}</a></b> перешёл по реферальной ссылке <b><a href="tg://user?id={5}">{4}{3}</a></b>\n#user_ref</i>'.format(nick, rasa, a, onick, orasa, referrer_candidate), parse_mode = 'html')
                await main.send_message(a, '<i>Вы перешли по реферальной ссылке <b><a href="tg://user?id={2}">{1}{0}</a></b></i>'.format(onick, orasa, referrer_candidate), parse_mode = 'html')
                await main.send_message(referrer_candidate, '<i>По вашей реферальной ссылке перешёл <b><a href="tg://user?id={2}">{1}{0}</a></b></i>'.format(nick, rasa, a), parse_mode = 'html')
                try:
                    cursor.execute('UPDATE userdata SET lootbox = lootbox+1 WHERE user_id = ?', (referrer_candidate,))
                    conn.commit()
                    await main.send_message(referrer_candidate, '<i>📦 Вам выдан 1 лутбокс</i>', parse_mode = 'html');
                except Exception as e:
                    await main.send_message(referrer_candidate, '<i><b>&#10060; Ошибка: </b>{0}</i>'.format(e), parse_mode = 'html');
            else:
                await main.send_message(a, '<i><b>&#10060; Произошли ошибки при переходе по реферальной ссылке: </b>\n{0}</i>'.format(err), parse_mode = 'html')
        else:
            a = message.from_user.id
            chid = message.chat.id
            cursor.execute('SELECT count(*) FROM clandata WHERE group_id = ?', (chid,))
            count = cursor.fetchone()[0]
            if count == 0:
                chn = message.chat.title
                markup = types.InlineKeyboardMarkup()
                buttons = types.InlineKeyboardButton(text='➕ Создать', callback_data='create_clan')
                markup.add(buttons)
                await main.send_message(chid, '<i>Создать клан <b>{0}</b></i>'.format(chn), parse_mode = 'html', reply_markup = markup)
            else:
                cursor.execute('SELECT name FROM clandata WHERE group_id=?', (chid,))
                chn = cursor.fetchone()[0]
                cursor.execute('SELECT bio FROM clandata WHERE group_id=?', (chid,))
                bio = cursor.fetchone()[0]
                markup = types.InlineKeyboardMarkup()
                buttons = types.InlineKeyboardButton(text='➕ Вступить/Выйти', callback_data='join_clan')
                markup.add(buttons)
                buttons = types.InlineKeyboardButton(text='👥 Участники клана', callback_data='clan_members')
                markup.add(buttons)
                buttons = types.InlineKeyboardButton(text='✏ Управление', callback_data='clan_settings')
                markup.add(buttons)
                buttons = types.InlineKeyboardButton(text='📣 Созвать клан', callback_data='call_clan')
                markup.add(buttons)
                markup.add(types.InlineKeyboardButton(text='🏗 Комнаты (постройки)', callback_data='clan_buildings'))
                cursor.execute('SELECT balance FROM clandata WHERE group_id = ?', (chid,))
                balance = cursor.fetchone()[0]
                cursor.execute('SELECT hqplace FROM clandata WHERE group_id = ?', (chid,))
                hqplace = cursor.fetchone()[0]
                cursor.execute('SELECT address FROM clandata WHERE group_id = ?', (chid,))
                address = cursor.fetchone()[0]
                cursor.execute('SELECT photo FROM clandata WHERE group_id = ?', (chid,))
                photo = cursor.fetchone()[0]
                leader = '&#127942; Топ кланов на данный момент:'
                cursor.execute('SELECT COUNT(*) FROM clandata WHERE (type=? AND balance < 1000000) OR group_id=-1001395868701', ('public',))
                count = cursor.fetchone()[0]
                cursor.execute('''SELECT * FROM clandata
                WHERE (type=? AND balance < 1000000) OR group_id=-1001395868701
                ORDER BY balance DESC
                LIMIT 10''', ('public',))
                for row in cursor:
                    leader+='\n<b><a href="{0}">{1}</a> - ${2}</b>'.format(row[8], row[1], row[4])
                prof = '<i>Клан <b>{0}</b>\n{4}&#128176; Баланс: <b>${1}</b>\n&#127970; Штаб-квартира: <b>{2}</b>\n{3}</i>'.format(chn, balance, '{0}, {1}'.format(hqplace, address) if hqplace != '' else 'отсутствует', leader if count!=0 else '', '\n{0}\n\n'.format(bio) if bio!='' else '')
                if photo=='':
                    await main.send_message(chid, prof, parse_mode = 'html', reply_markup = markup)
                else:
                    try:
                        await main.send_photo(chid, photo, caption=prof, parse_mode = 'html', reply_markup = markup)
                    except:
                        await main.send_message(chid, prof, parse_mode = 'html', reply_markup = markup)
    except Exception as e:
        await main.send_message(chid, '<i><b>&#10060; Ошибка: </b>{0}</i>'.format(e), parse_mode = 'html')