from aiogram import Bot, Dispatcher

import configparser

config = configparser.ConfigParser()
config.read(".config")
config.__setattr__("altToken", config.get("alt", "token"))
config.__setattr__("stripeTest", config.get("alt", "StripeTest"))

bot = Bot(
    token=config.altToken, 
    parse_mode='html', 
    disable_web_page_preview=True
)
dp = Dispatcher(bot)

PPT = config.stripeTest # Payments Provider Token