import sys
import getpass

from datetime import datetime
from configparser import ConfigParser

from aiogram import Bot, Dispatcher

def _colored_input(prompt: str = "", hide: bool = False) -> str:
    frame = sys._getframe(1)
    return (getpass if hide else input)(
        "\x1b[32m{time:%Y-%m-%d %H:%M:%S}.000\x1b[0m | "
        "\x1b[1m{level: <8}\x1b[0m | "
        "\x1b[36m{name}\x1b[0m:\x1b[36m{function}\x1b[0m:\x1b[36m{line}\x1b[0m - \x1b[1m{prompt}\x1b[0m".format(
            time=datetime.now(),
            level="INPUT",
            name=frame.f_globals["__name__"],
            function=frame.f_code.co_name,
            line=frame.f_lineno,
            prompt=prompt,
        )
    )

config = ConfigParser(allow_no_value=False)

if not config.read("./.config"):
    config["core"] = {
        "token": _colored_input("Enter your bot API TOKEN: "),
        "payments": _colored_input("Enter your Payments Provider TOKEN: ")
    }
    with open('./.config', 'w') as file:
        config.write(file)

config.__setattr__("token", config.get("core", "token"))
config.__setattr__("PPT", config.get("core", "payments"))
config.__setattr__("altToken", config.get("alt", "token"))
config.__setattr__("altPPT", config.get("alt", "payments"))

is_alt = _colored_input("Do you want to start alt bot? (y/n): ")
is_alt = is_alt == "y"

bot = Bot(
    token=config.altToken if is_alt else config.token, 
    parse_mode='html', 
    disable_web_page_preview=True
)
dp = Dispatcher(bot)

PPT = config.altPPT if is_alt else config.PPT  # Payments Provider Token