from aiogram import Bot, Dispatcher

TOKEN = '6013919640:AAHd1ShmwsLvcM1x8HYiQaDNGJxZcehsOhQ'  #токен бота
 
bot = Bot(
    token=TOKEN, 
    parse_mode='html', 
    disable_web_page_preview=True
)
dp = Dispatcher(bot)