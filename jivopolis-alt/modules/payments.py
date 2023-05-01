from .. import PPT, bot, dp, cur, tglog, get_embedded_link
from aiogram.dispatcher.filters import Text
from aiogram.types import LabeledPrice, ContentTypes, Message, ShippingQuery, PreCheckoutQuery, CallbackQuery


# Setup prices
prices = [
    LabeledPrice(label='☕️ Тюленям на чай', amount=200),
    LabeledPrice(label='💸 10 000 Живокоинов', amount=100),
]

@dp.callback_query_handler(Text(equals="donate"))
async def cmd_buy(call: CallbackQuery):
    await bot.send_invoice(
        call.message.chat.id, 
        payload="cup-of-tea",
        title='☕️ Тюленям на чай',
        description="Этим вы поддерживаете разработку живополиса, даёте разработчикам деньги на жизнь, а также задабриваете их и даёте мотивацию творить дальше.",
        provider_token=PPT,
        currency='usd',
        prices=prices,
        suggested_tip_amounts=[100, 300, 500, 1000],
        max_tip_amount=2500,
        start_parameter='cup-of-tea',
    )


@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(
        pre_checkout_query.id, 
        ok=True,
        error_message="⚒ Что-то пошло не так. Повторите ещё раз."
    )


@dp.message_handler(content_types=ContentTypes.SUCCESSFUL_PAYMENT)
async def got_payment(message: Message):
    cur.update("userdata").set(balance="column 10000").where(user_id=message.from_user.id).commit()
    await bot.send_message(
        message.chat.id,
        f'🍩 Только что вы оставили <code>{message.successful_payment.total_amount / 100} {message.successful_payment.currency}</code> админам на чай.'
        "\n\n🥰 Большое вам спасибо! За это мы предоставляем вам скромненькую благодарность в виде <code>10 000 живокоинов</code>",
    )
    await tglog(f"🍩 Только что {await get_embedded_link(message.from_user.id)} оставил <code>{message.successful_payment.total_amount / 100} {message.successful_payment.currency}</code> админам на чай.", "#donate")
