import sqlite3
import random
from typing import Union

from loguru import logger

from ..bot import bot
from ..misc import current_time, log_error
from ..config import limiteds, CREATOR, levelrange, leveldesc, ITEMS, log_chat, ach

from aiogram.types import InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, User

def connect_database() -> None:
    global conn, cur
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    if conn:
        return logger.success('database connected')
    return logger.critical('database is not connected')

async def check(user_id, chat_id) -> None:
        try:
            lastfill = current_time() - cur.execute('SELECT lastfill FROM globaldata').fetchone()

            if lastfill >= 86400:
                for item in limiteds:
                    cur.execute(f'UPDATE globaldata SET {item}={random.randint(5, 15)}')
                cur.execute(f"UPDATE globaldata SET lastfill={current_time()}")

            cur.execute(f'UPDATE userdata SET lastseen={current_time()} WHERE user_id={user_id}')
            conn.commit()

            points = cur.execute(f'SELECT points FROM userdata WHERE user_id={user_id}').fetchone()

            if user_id == CREATOR:
                cur.execute(f'UPDATE userdata SET rang=3 WHERE user_id={user_id}')
                conn.commit()

            lastelec = current_time() - cur.execute(f'SELECT lastelec FROM userdata WHERE user_id={user_id}').fetchone()

            if lastelec > 86400:
                cur.execute(f'UPDATE userdata set electimes=0 WHERE user_id={user_id}')
                conn.commit()

                cur.execute(f'UPDATE userdata set lastelec={current_time()} WHERE user_id={user_id}')
                conn.commit()

            lvl = cur.execute(f'SELECT level FROM userdata WHERE user_id={user_id}').fetchone()

            if lvl > len(levelrange): 
                return
            elif points >= levelrange[lvl] and points < levelrange[lvl+1]:
                return

            for i in levelrange: #todo recreate
                if points >= i and levelrange.index(i) >= len(levelrange) - 1 and lvl != levelrange.index(i):
                    cur.execute('UPDATE userdata SET lvl=? WHERE user_id=?', (levelrange.index(i), user_id,))
                    conn.commit()

                    try:
                        return await bot.send_message(user_id, f'<i>&#128305; Теперь ваш уровень в Живополисе: <b>{levelrange.index(i)}</b>\nПоздравляем!\n{leveldesc[levelrange.index(i)]}</i>', parse_mode='html')
                    except Exception as e:
                        return await bot.send_message(chat_id, f'<i>&#128305; Теперь ваш уровень в Живополисе: <b>{levelrange.index(i)}</b>\nПоздравляем!\n{leveldesc[levelrange.index(i)]}</i>'.format(levelrange.index(i), leveldesc[levelrange.index(i)]), parse_mode='html')
                        
                if points>=i and points<levelrange[levelrange.index(i)+1] and lvl!=levelrange.index(i):
                    cur.execute('UPDATE userdata SET lvl=? WHERE user_id=?', (levelrange.index(i), user_id,))
                    conn.commit()
                    try:
                        return await bot.send_message(user_id, '<i>&#128305; Теперь ваш уровень в Живополисе: <b>{0}</b>\nПоздравляем!\n{1}</i>'.format(levelrange.index(i), leveldesc[levelrange.index(i)]), parse_mode='html')
                    except Exception as e:
                        return await bot.send_message(chat_id, '<i>&#128305; Теперь ваш уровень в Живополисе: <b>{0}</b>\nПоздравляем!\n{1}</i>'.format(levelrange.index(i), leveldesc[levelrange.index(i)]), parse_mode='html')

        except Exception as e:
            if 'NoneType' in str(e):
                pass
            else:
                return logger.exception(e)

async def db_table_val(user_id, user_name, user_surname, username, balance, cansteal, nick, bio, rasa, temp, morj, mask, ready, battles, chn):
        cur.execute('INSERT INTO userdata (user_id, user_fullname, username, balance, cansteal, nick, desc, rasa, temp, morj, mask, ready, battles, clanname) VALUES ({user_id}, , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (user_id, user_name, user_surname, username, balance, cansteal, nick, bio, rasa, temp, morj, mask, ready, battles, chn,))
        conn.commit()

def itemdata(user_id, item) -> Union[str, None, InlineKeyboardButton]:      #migrate to new ITEMS list          
    try: 
        items = cur.execute(f"SELECT {item} FROM userdata WHERE user_id={user_id}").fetchone()

        if items > 0:      
            item_index = ITEMS[1].index(items)             
            return InlineKeyboardButton(text=f'{ITEMS[0][item_index]} {items}', callback_data=ITEMS[1][item_index])
                
        else:      
            return 'emptyslot'           
    except Exception as e:         
        return logger.exception(e)

async def eat(call: CallbackQuery, food: str, heal) -> None:
    user_id = call.from_user.id
    chat = call.message.chat.id

    try:
        health = cur.execute(f'SELECT health FROM userdata WHERE user_id={user_id}').fetchone()
        food_amount = cur.execute(f'SELECT {food} FROM userdata WHERE user_id={user_id}').fetchone()

        if food_amount < 1:
            return await call.answer(text='❌ У вас нет такой еды', show_alert = True)

        cur.execute(f'UPDATE userdata SET {food}={food}-1 WHERE user_id={user_id}')
        conn.commit()

        cur.execute(f'UPDATE userdata SET health=health+{heal} WHERE user_id={user_id}')
        conn.commit()

        if heal > 0:
            await call.answer(text=f'❤ +{heal} HP на здоровье!', show_alert = True)
        else:
            await call.answer(text='🤢 Зачем я это съел? Теперь мне нехорошо', show_alert = True)
            health = cur.execute(f'SELECT health FROM userdata WHERE user_id={user_id}').fetchone()

            if health < 1:
                await bot.send_message(chat, '<i>&#9760; Вы умерли</i>', parse_mode='html')

    except Exception as e:
        await bot.send_message(chat, '&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
        await bot.send_message(chat, '<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')

async def create_acc(user:  User, chat_id: str):
    try:
        count = cur.execute('SELECT COUNT(*) FROM userdata WHERE user_id=?', (user.id,)).fetchone()

        if count > 0:
            return await bot.send_message(chat_id, '<i>Вы уже создавали аккаунт</i>', parse_mode = 'html', reply_markup = ReplyKeyboardRemove())
            
        await db_table_val(user_id=user.id, user_name=user.first_name, user_surname=user.last_name,
        username=user.username, balance=0, cansteal=1, nick = user.first_name, bio = 'пусто',
        rasa = '&#128529;', temp = '&#128529;', morj = 0, mask = '', ready = 0, battles = 0, chn = '')
        conn.commit()

        await bot.send_message(log_chat, f'<i><b><a href="tg://user?id={user.id}">{user.full_name}</a></b> присоединился(-ась) к Живополису\n#user_signup</i>', parse_mode='html', disable_web_page_preview=True)
        
        cur.execute(f'UPDATE userdata SET register_date = {current_time()} WHERE user_id={user.id}')
        conn.commit()

    except Exception as e:
        if str(e).startswith('UNIQUE constraint failed: '):
            await bot.send_message(chat_id, '<i>Вы уже создавали аккаунт</i>', parse_mode = 'html', reply_markup = ReplyKeyboardRemove())
        elif str(e) == 'database is locked':
            await bot.send_message(chat_id, '<i><b>&#10060; Ошибка: </b>база данных заблокирована</i>', parse_mode = 'html', reply_markup = ReplyKeyboardRemove())
        else:
            log_error(e)
    else:
        await bot.send_message(chat_id, '<i>&#9989; Вы были добавлены в базу данных</i>', parse_mode = 'html', reply_markup = ReplyKeyboardRemove())

async def poison(user_id: str, target_id: str, chat_id: str) -> None:
    try:
        my_health = cur.execute(f'SELECT health FROM userdata WHERE user_id={user_id}').fetchone()

        if my_health < 0:
            return await bot.send_message(chat_id, '<i>&#9760; Вы умерли. Попросите кого-нибудь вас воскресить</i>', parse_mode = 'html')

        poison = cur.execute(f'SELECT poison FROM userdata WHERE user_id={user_id}').fetchone()

        if poison < 1:
            return await bot.send_message(chat_id, '<i>&#10060; У вас нет яда. Возможно, это к лучшему</i>', parse_mode='html')

        cur.execute(f'UPDATE userdata SET poison=poison-1 WHERE user_id={user_id}')
        conn.commit()

        nick = cur.execute(f'SELECT nick FROM userdata WHERE user_id={user_id}').fetchone()
        rasa = cur.execute(f'SELECT rasa FROM userdata WHERE user_id={user_id}').fetchone()

        target_nick = cur.execute(f'SELECT nick FROM userdata WHERE user_id={target_id}').fetchone()
        target_rasa = cur.execute(f'SELECT rasa FROM userdata WHERE user_id={target_id}').fetchone()
        target_health = cur.execute(f'SELECT health FROM userdata WHERE user_id={target_id}').fetchone()

        random_damage = random.randint(50, 200)
        done = random.choice([True, False])

        if done:
            cur.execute(f'UPDATE userdata SET health=health-{random_damage} WHERE user_id={target_id}')
            conn.commit()

            await bot.send_message(log_chat, f'<i><b><a href="tg://user?id={user_id}">{rasa}{nick}</a></b> отравил <b><a href="tg://user?id={target_id}">{target_rasa}{target_nick}</a></b>.\n#user_poison</i>', parse_mode='html')
            await bot.send_message(chat_id, f'<i>&#129514; Вы отравили <b><a href="tg://user?id={target_id}">{target_rasa}{target_nick}</a></b></i>', parse_mode='html')
            await bot.send_message(target_id, f'<i>&#129514; Вас отравил <b><a href="tg://user?id={user_id}">{rasa}{nick}</a></b></i>', parse_mode='html')
        else:
            return await bot.send_message(chat_id, '<i>&#10060; Неудача. Возможно, это к лучшему.\nЯд потрачен зря</i>', parse_mode='html')

    except Exception as e:
        await bot.send_message(chat_id, '&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
        await bot.send_message(chat_id, f'<i><b>Текст ошибки: </b>{e}</i>', parse_mode = 'html')
        return logger.exception(e)

async def shoot(user_id: str, target_id: str, chat_id: str) -> None: #todo NO OTH
        try:
            my_health = cur.execute(f'SELECT health FROM userdata WHERE user_id={user_id}')

            if my_health < 0:
                return await bot.send_message(chat_id, '<i>&#9760; Вы умерли. Попросите кого-нибудь вас воскресить</i>', parse_mode = 'html')

            gun = cur.execute(f'SELECT gun FROM userdata WHERE user_id={user_id}').fetchone()

            if gun < 1:
                return await bot.send_message(chat_id, '<i>&#10060; У вас нет пистолета. Возможно, это к лучшему</i>', parse_mode='html')

            health = cur.execute(f'SELECT health FROM userdata WHERE user_id={target_id}').fetchone()

            cur.execute(f'UPDATE userdata SET gun=gun-1 WHERE user_id={user_id}')
            conn.commit()

            nick = cur.execute(f'SELECT nick FROM userdata WHERE user_id={user_id}').fetchone()
            rasa = cur.execute(f'SELECT rasa FROM userdata WHERE user_id={user_id}').fetchone()
            
            target_nick = cur.execute(f'SELECT nick FROM userdata WHERE user_id={target_id}').fetchone()
            target_rasa = cur.execute(f'SELECT rasa FROM userdata WHERE user_id={target_id}').fetchone()

            rand = random.randint(100,200)
            done = random.choice([True, False])

            if done:
                cur.execute(f'UPDATE userdata SET health=health-{rand} WHERE user_id={target_id}')
                conn.commit()

                await bot.send_message(log_chat, f'<i><b><a href="tg://user?id={user_id}">{rasa}{nick}</a></b> застрелил <b><a href="tg://user?id={target_id}">{target_rasa}{target_nick}</a></b>\n#user_gunshoot</i>', parse_mode='html')
                await bot.send_message(chat_id, f'<i>&#128299; Вы застрелили <b><a href="tg://user?id={target_id}">{target_rasa}{target_nick}</a></b></i>', parse_mode='html')
                await bot.send_message(target_id, f'<i>&#128299; Вас застрелил <b><a href="tg://user?id={user_id}">{rasa}{nick}</a></b></i>', parse_mode='html')
                
                prison = random.choice([True, False])

                if prison:
                    cur.execute(f'UPDATE userdata SET prison={current_time() + 1200} WHERE user_id={user_id}')
                    conn.commit()

                    await bot.send_message(chat_id, f'<i>&#128110; Господин <b><a href="tg://user?id={user_id}">{rasa}{nick}</a></b>, вы задержаны за убийство огнестрельным оружием. Пройдёмте в отделение.\n\nВы были арестованы на <b>20 минут</b></i>', parse_mode='html')
            else:
                await bot.send_message(chat_id, f'<i>&#10060; Вы выстрелили мимо. Возможно, это к лучшему.\nПистолет потрачен зря</i>', parse_mode='html')
        
        except Exception as e:
            await bot.send_message(chat_id, '&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
            await bot.send_message(chat_id, f'<i><b>Текст ошибки: </b>{e}</i>', parse_mode = 'html')

async def achieve(user_id: str, chat_id : str, achievement: str) -> None: #todo new ACHIEVEMENTS
    try:
        achieve = cur.execute(f'SELECT {achievement} FROM userdata WHERE user_id={user_id}').fetchone()
        
        if achieve != 0:
            return

        index = ach[0].index(achievement)
        name = ach[1][index]
        desc = ach[2][index]
        money = ach[3][index]
        points = ach[4][index] #todo WHY POINTS. ITS XP

        cur.execute(f'UPDATE userdata SET {achievement} = 1 WHERE user_id = {user_id}')
        conn.commit()

        rasa = cur.execute(f'SELECT rasa FROM userdata WHERE user_id = {user_id}').fetchone()
        nick = cur.execute(f'SELECT nick FROM userdata WHERE user_id = {user_id}').fetchone()

        cur.execute(f'UPDATE userdata SET balance = balance + {money} WHERE user_id = {user_id}')
        conn.commit()
        cur.execute(f'UPDATE userdata SET points = points+{points} WHERE user_id = {user_id}')
        conn.commit()

        chat_type = await bot.get_chat(chat_id)
        chat_type = chat_type.type

        if chat_type == 'private':
            await bot.send_message(chat_id, f'<i>У вас новое достижение: <b>{name}</b>\n{desc}. \nВаша награда: <b>${money}</b> и &#128161; <b>{points}</b> очков</i>', parse_mode = 'html')
        else:
            await bot.send_message(chat_id, f'<i><b><a href="tg://user?id={user_id}">{rasa}{nick}</a></b>, у вас новое достижение: <b>{name}</b>\n{desc}. \nВаша награда: <b>${money}</b> и &#128161; <b>{points}</b> очков</i>', parse_mode = 'html')
    except Exception as e:
        await bot.send_message(chat_id, '&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
        await bot.send_message(chat_id, '<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')

async def cure(user_id: str, target_id: str, chat_id: str) -> None:
    try:
        nerr = 0
        medicine = cur.execute(f'SELECT medicine FROM userdata WHERE user_id={user_id}').fetchone()

        if medicine < 1:
            return await bot.send_message(chat_id, '<i>&#10060; У вас нет таблеток(</i>', parse_mode='html')
            
        health = cur.execute(f'SELECT health FROM userdata WHERE user_id={target_id}').fetchone()

        nick = cur.execute(f'SELECT nick FROM userdata WHERE user_id={user_id}').fetchone()

        rasa = cur.execute(f'SELECT rasa FROM userdata WHERE user_id={user_id}').fetchone()
        target_nick = cur.execute(f'SELECT nick FROM userdata WHERE user_id={target_id}').fetchone()
        target_rasa = cur.execute(f'SELECT rasa FROM userdata WHERE user_id={target_id}').fetchone()

        if health > 0 and health < 100:
            cur.execute(f'UPDATE userdata SET medicine=medicine-1 WHERE user_id={user_id}')
            conn.commit()

            rand = random.randint(1, 100-health)

            cur.execute(f'UPDATE userdata SET health=health+{rand} WHERE user_id={target_id}')
            conn.commit()

            nick = cur.execute(f'SELECT nick FROM userdata WHERE user_id={user_id}').fetchone()
            rasa = cur.execute(f'SELECT rasa FROM userdata WHERE user_id={user_id}').fetchone()

            target_nick = cur.execute(f'SELECT nick FROM userdata WHERE user_id={target_id}').fetchone()
            target_rasa = cur.execute(f'SELECT rasa FROM userdata WHERE user_id={target_id}').fetchone()
            
            if target_id == user_id:
                return await bot.send_message(chat_id, '<i>&#128138; Успех! Вы вылечили себя</i>', parse_mode='html')
            else:
                await bot.send_message(chat_id, f'<i>&#128138; Успех! Вы вылечили <b><a href="tg://user?id={target_id}">{target_rasa}{target_nick}</a></b></i>', parse_mode='html')
                await bot.send_message(target_id, f'<i>&#128138; Вас вылечил <b><a href="tg://user?id={user_id}">{rasa}{nick}</a></b></i>', parse_mode='html')
                nerr = 1

        elif health >= 100:
            if target_id != user_id:
                return await bot.send_message(chat_id, f'<i>&#128138; <b><a href="tg://user?id={target_id}">{target_rasa}{target_nick}</a></b> полностью здоров, зачем вам тратить лекарства впустую?\nЛекарства <b>не потрачены</b></i>', parse_mode='html')   
            else:
                return await bot.send_message(chat_id, f'<i>&#128138; Вы полностью здоровы, зачем вам тратить лекарства впустую?\nЛекарства <b>не потрачены</b></i>', parse_mode='html')        
        else:
            if target_id == user_id:
                return await bot.send_message(chat_id, '<i>&#10060; Вы не можете воскресить самого себя</i>', parse_mode='html')
                
            cur.execute(f'UPDATE userdata SET medicine=medicine-1 WHERE user_id={user_id}')
            conn.commit()

            rand = random.randint(50,100)

            cur.execute(f'UPDATE userdata SET health={rand} WHERE user_id={target_id}')
            conn.commit()

            nick = cur.execute(f'SELECT nick FROM userdata WHERE user_id={user_id}').fetchone()
            rasa = cur.execute(f'SELECT rasa FROM userdata WHERE user_id={user_id}').fetchone()

            target_nick = cur.execute(f'SELECT nick FROM userdata WHERE user_id={target_id}').fetchone()
            target_rasa = cur.execute(f'SELECT rasa FROM userdata WHERE user_id={target_id}').fetchone()

            await bot.send_message(chat_id, f'<i>&#128138; Успех! Вы воскресили <b><a href="tg://user?id={target_id}">{target_rasa}{target_nick}</a></b></i>', parse_mode='html')
            nerr = 1
            await bot.send_message(target_id, f'<i>&#128138; Вас воскресил <b><a href="tg://user?id={user_id}">{rasa}{nick}</a></b></i>', parse_mode='html')
            
            await achieve(user_id, chat_id, 'helper')

        if nerr == 1:
            cur.execute(f"UPDATE userdata SET cured=cured+1 WHERE user_id={user_id}")
            conn.commit()

            cured = cur.execute(f"SELECT cured FROM userdata WHERE user_id={user_id}").fetchone()

            if cured >= 20:
                await achieve(user_id, chat_id, 'medquest')
                cur.execute(f"UPDATE userdata SET medic=medic+1 WHERE user_id={user_id}")
                conn.commit()
                await bot.send_message(chat_id, '<i>Вы получаете <b>🩺 Стетоскоп</b>. Эта маска будет показывать всем, что вы профессиональный врач, и вам можно доверять</i>', parse_mode = 'html')

    except Exception as e:
        await bot.send_message(chat_id, '&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>', parse_mode='html')
        await bot.send_message(chat_id, '<i><b>Текст ошибки: </b>{0}</i>'.format(e), parse_mode = 'html')