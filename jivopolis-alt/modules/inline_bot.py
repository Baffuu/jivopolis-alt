import contextlib
from ..database.functions import cur, conn, check, SUPPORT_LINK, get_mask, get_link, log_chat
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup, ChosenInlineResult
from aiogram import Dispatcher
from .. import logger, bot


async def inline_mode(query: InlineQuery):
    try:
        user_id = query.from_user.id
        await check(user_id, user_id)
        results = []
        try:
            health: int = cur.execute(f"SELECT health FROM userdata WHERE user_id={query.from_user.id}").fetchone()[0]
            is_banned = bool(cur.execute(f"SELECT is_banned FROM userdata WHERE user_id={query.from_user.id}").fetchone()[0])
        except TypeError:
            return 

        if is_banned:
            return await bot.answer_inline_query(
                query.id, 
                [
                    InlineQueryResultArticle(
                        id = 'banned',
                        title = '🧛🏻‍♂️ Вы были забаненны в боте.',
                        description = 'Если вы считаете, что это - ошибка, обратитесь в поддержку.',
                        input_message_content = 
                        InputTextMessageContent(
                            f'🧛🏻‍♂️ Вы были забаненны в боте. Если вы считаете, что это - ошибка, обратитесь в <a href="{SUPPORT_LINK}">поддержку</a>.'
                        )
                    )
                ]
            )

        if health < 0:
            return await bot.answer_inline_query(query.id, [InlineQueryResultArticle(
                id = 'dead',
                title = '☠️ Вы умерли',
                description = 'Попросите кого-нибудь вас воскресить',
                input_message_content = InputTextMessageContent('<i>☠️ Вы умерли. Попросите кого-нибудь вас воскресить</i>')
            )])

        data = query.query 

        try:
            nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id={user_id}").fetchone()[0]
            mask = get_mask(user_id)
            balance = cur.execute(f"SELECT balance FROM userdata WHERE user_id={user_id}").fetchone()[0] 
        except TypeError:
            results.append(InlineQueryResultArticle(
                id = 'account_not_found',
                title = '👤 Аккаунт не найден',
                description = 'Попробуйте зайти в бота и создать новый!',
                input_message_content = InputTextMessageContent('🐸 Ваш аккаунт не найден. Нажмите на кнопку ниже чтобы его создать.'),
                reply_markup = InlineKeyboardButton("Создать аккаунт", callback_data="sign_up")
            ))
            data = None
        
        match(data):
            case None:
                pass
            case give if give.startswith('$'):
                try:
                    money = int(data[1:])
                except:
                    money = None
                    
                markup = InlineKeyboardMarkup()
                try:
                    if money > 0:
                        if balance >= money:
                            markup.add(InlineKeyboardButton(text='💲 Забрать деньги', callback_data=f'check_{money}'))
                            results.append(InlineQueryResultArticle(
                                id = f'check_{money}',
                                title = f'💲 Отправить чек на сумму ${money}',
                                description = f'Баланс: ${balance}',
                                input_message_content=InputTextMessageContent(f'<i>&#128178; <b><a href="tg://user?id={user_id}">{mask}{nick}</a></b> предлагает вам <b>${money}</b></i>'),
                                reply_markup = markup,
                            ))
                        else:
                            markup.add(InlineKeyboardButton(text='💲 Забрать деньги', callback_data=f'check_{balance}'))
                            results.append(InlineQueryResultArticle(
                                id = f'check_{balance}',
                                title = f'💲 Отправить чек на сумму ${balance}',
                                description = f'Баланс: ${balance}',
                                input_message_content=InputTextMessageContent(f'<i>&#128178; <b><a href="{get_link(user_id)}">{mask}{nick}</a></b> предлагает вам <b>${balance}</b></i>'),
                                reply_markup = markup,
                            ))
                except TypeError:
                    results.append(InlineQueryResultArticle(
                        id = 'check_error',
                        title = '🚫 Введите правильное число',
                        description = 'это должно быть целое число, не текст и не десятичное.',
                        input_message_content = InputTextMessageContent('🚫 Введите правильное число'),
                    ))
        return await bot.answer_inline_query(query.id, results, 1)
    except Exception as e:
        logger.exception(e)


async def on_pressed_inline_query(inline: ChosenInlineResult):
    with contextlib.suppress(Exception):
        user_id = inline.from_user.id
        nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id={user_id}").fetchone()[0]
        mask = get_mask(user_id)
        data = inline.query

        if data.startswith('$'):
            money = int(data[1:])
            if money > 0:
                cur.execute(f"UPDATE userdata SET balance = balance - {money} WHERE user_id={user_id}"); conn.commit()
                await bot.send_message(log_chat, f'<i>&#128178; <b><a href="{get_link(user_id)}">{mask}{nick}</a></b> выписал чек на <b>${money}</b>\n#user_check</i>')
            if money < 0:
                await bot.send_message(log_chat, f'<i>&#128178; <b><a href="{get_link(user_id)}">{mask}{nick}</a></b> выставил счёт на <b>${money}</b>\n#user_bill</i>')
    

def register(dp: Dispatcher):
    dp.register_inline_handler(inline_mode)
    dp.register_chosen_inline_handler(on_pressed_inline_query)