from dataclasses import dataclass
from typing import Literal, Union, Optional

@dataclass
class Item():
    name: str
    ru_name: str
    emoji: Optional[str] = '🌀'
    cost: Optional[int] = None
    type: Optional[str] = None
    type_param: Union[str, int, list] = None
    description: Optional[str] = None

    @property 
    def price(self) -> Union[int, Literal['no cost']]:
        '''
        You can get cost (or price) of the item 
        '''

        return 'no cost' if self.cost < 0 or not self.cost else self.cost


ITEMS = {
    'walrus': Item(
                name='seal', 
                ru_name='Тюлень', 
                emoji='🦭', 
                cost=1000, 
                type='mask',
                description='очень любят баны'
    ),
    
    'lootbox': Item(
                name='lootbox', 
                ru_name='Лутбокс',
                emoji='📦',
                type='lootbox',
                description='в нём может быть что-то интересное'
    ),
    
    'cow': Item(
                name='cow',
                ru_name='Корова',
                cost=250,
                emoji='🐄',
                type='mask',
                type_param='can_get_milk',
                description='даёт молоко, но только на ферме'
    ),

    'key': Item(
            name='key',
            ru_name='Ключ',
            emoji='🗝️',
            type='key',
            description='Очень старый ключ. Кто знает, может быть однажды он пригодится…'
    ),

    'gun': Item(
            name='gun',
            ru_name='Пистолет',
            emoji='🔫',
            type='robber',
            cost=1000,
            description='Водный пистолет. Кажется, его потерял какой-то ребёнок.',
    ),

    'wolf': Item(
        name='wolf',
        ru_name='Волк',
        emoji='🐺',
        type='mask',
        cost=500,
        description='слабее льва и тигра, но волк не выступает в цирке ☝'
    ),

    'vest': Item(
        name='vest',
        ru_name='Бронежилет',
        emoji='🦺',
        type='robber',
        cost=1000,
        description='спасёт от пистолета. Или нет...'
    ),

    'japanese_goblin': Item(
        name='japanese_goblin',
        ru_name='Маска Тенгу',
        cost=5000,
        emoji='👺',
        type='robber',
        description='её нельзя надеть'
    ),

    'ninja': Item(
        name='ninja',
        ru_name='Ниндзя',
        cost=2000,
        emoji='🥷',
        type='robber',
        description='древний китайский ниндзя, которому уже много-много лет…\n\n**китайская партия одобряет'
    ),

    'bomb': Item(
        name='bomb',
        ru_name='Бомбa',
        emoji='💣',
        cost=650,
        type='robber',
        description='бум'
    ),

    'confetti': Item(
        name='confetti',
        ru_name='Конфетти',
        emoji='🎊',
        cost=50,
        type='mask',      
    ),

    'pill': Item(
        name='pill',
        ru_name='Таблетка',
        emoji='💊',
        cost=500,
        type='medicine',
    ),

    'fireworks': Item(
        name='fireworks',
        ru_name="Фейерверки",
        emoji='🎆',
        cost=100,
        type='mask'
    ),

    'party_pooper': Item(
        name='party_pooper',
        ru_name='Хлопушка',
        emoji='🎉',
        cost=50,
        type='mask'
    ),

    'window': Item(
        name='window',
        ru_name='Окно',
        emoji='🪟',
        cost=400,
        type='building_material',
    ),

    'brick': Item(
        name='brick',
        ru_name='Кирпич',
        emoji='🧱',
        cost=100
    ),

    'door': Item(
        name='door',
        ru_name='Дверь',
        emoji='🚪',
        cost=500,
    ),

    'fox': Item(
        name='fox',
        ru_name='Лиса',
        emoji='🦊',
        cost=100,
        type='mask',
    ),

    'party_popper': Item(
        name='party_popper',
        ru_name='Хлопушка',
        emoji='🎉',
        cost=50,
        type='mask',
    ),

    'baguette': Item(
        name='baguette', 
        ru_name='Багет', 
        emoji='🥖',
        cost=25, 
        type='food'
    ),

    'apple': Item(
        name='apple', 
        ru_name='Яблоко', 
        cost=50, 
        type='food',
    ),

    'doughnut': Item(
        name='doughnut', 
        ru_name='Пончик', 
        emoji='🍩',
        cost=10, 
        type='food',
    ),

    'fries': Item(
        name='fries', 
        ru_name='Картофель Фри', 
        emoji='🍟', 
        cost=10, 
        type='food'
    ),

    'ice_cream': Item(
        name='ice_cream',
        ru_name='Мороженое',
        emoji='🍨',
        cost=250, 
        type='food'
    ),

    'shaved_ice': Item(
        name='shaved_ice', 
        ru_name='Фруктовый лед', 
        emoji='🍧', 
        cost=41, 
        type='food'
    ),

    'fairy': Item(
        name='fairy', 
        ru_name='Фея', 
        emoji='🧚', 
        cost=-1, 
        type='mask'
    ),

    'kiwi': Item(
        name='kiwi', 
        ru_name='Kиви', 
        emoji='🥝', 
        cost=10, 
        type='food'
    ),

    'ramen': Item(
        name='ramen', 
        ru_name='Рамен', 
        emoji='🍜', 
        cost=25, 
        type='food'
    ),

    'gold_medal': Item(
        name='gold_medal',
        ru_name='Золотая медаль',
        emoji='🥇',
        cost=-1,
        type='mask',
    ),

    'silver_medal': Item(
        name='silver_medal', 
        ru_name='Серебренная медаль', 
        emoji='🥈', 
        cost=-1, 
        type='mask'
    ),

    'bronze_medal': Item(
        name='bronze_medal', 
        ru_name='Бронзовая медаль', 
        emoji='🥉', 
        cost=-1, 
        type='mask'
    ),

    'mrs_claus': Item(
        emoji='🤶',
        name='mrs_claus',
        ru_name='Миссис Клаус',
        cost=75,
        type='mask'
    ),

    'santa_claus': Item(
        emoji='🎅',
        name='santa_claus',
        ru_name='Санта Клaус',
        cost=100,
        type='mask'
    ),

    'snowflake': Item(
        emoji='❄️',
        name='snowflake',
        ru_name='Снежинка',
        cost=30,
        type='mask'
    ),


    'snowman': Item(
        emoji='☃️',
        name='snowman',
        ru_name='Снеговик',
        cost=50,
        type='mask'
    ),


    'hedgehog': Item(
        emoji='🦔',
        name='hedgehog',
        ru_name='Еж',
        cost=100,
        type='mask'
    ),


    'truck': Item(
        emoji='🚚',
        name='truck',
        ru_name='Грузовик',
        cost=3000,
        type='mask'
    ),


    'poison': Item(
        emoji='🧪',
        name='poison',
        ru_name='Яд',
        cost=4000,
        type='robber'
    ),


    'milk': Item(
        emoji='🥛',
        name='milk',
        ru_name='Молоко',
        cost=25,
        type='food'
    ),


    'pelmeni': Item(
        emoji='🍲',
        name='pelmeni',
        ru_name='Пельмени',
        cost=50,
        type='food'
    ),


    'shawarma': Item(
        emoji='🌯',
        name='shawarma',
        ru_name='Шаурма',
        cost=25,
        type='food'
    ),


    'burger': Item(
        emoji='🍔',
        name='burger',
        ru_name='Бургер',
        cost=500,
        type='food'
    ),


    'pizza': Item(
        emoji='🍕',
        name='pizza',
        ru_name='Пицца',
        cost=200,
        type='food'
    ),


    'coconut': Item(
        emoji='🥥',
        name='coconut',
        ru_name='Кокос',
        cost=25,
        type='food'
    ),


    'tomato': Item(
        emoji='🍅',
        name='tomato',
        ru_name='Помидор',
        cost=10,
        type='food'
    ),


    'cucumber': Item(
        emoji='🥒',
        name='cucumber',
        ru_name='Огурец',
        cost=10,
        type='food'
    ),


    'spaghetti': Item(
        emoji='🍝',
        name='spaghetti',
        ru_name='Спагетти',
        cost=10,
        type='food'
    ),


    'bento': Item(
        emoji='🍱',
        name='bento',
        ru_name='Бенто',
        cost=500,
        type='food'
    ),


    'beer': Item(
        emoji='🍺',
        name='beer',
        ru_name='Пиво',
        cost=200,
        type='food'
    ),


    'meat_on_bone': Item(
        emoji='🍖',
        name='meat_on_bone',
        ru_name='Мясо на кости',
        cost=200,
        type='food'
    ),


    'cheburek': Item(
        emoji='🥟',
        name='cheburek',
        ru_name='Чeбурек',
        cost=50,
        type='food'
    ),


    'tea': Item(
        emoji='🍵',
        name='tea',
        ru_name='Чай',
        cost=50,
        type='food'
    ),


    'coffee': Item(
        emoji='☕',
        name='coffee',
        ru_name='Кофе',
        cost=50,
        type='food'
    ),


    'rice': Item(
        emoji='🍚',
        name='rice',
        ru_name='Рис',
        cost=70,
        type='food'
    ),


    'cookie': Item(
        emoji='🍪',
        name='cookie',
        ru_name='Печенье',
        cost=20,
        type='food'
    ),


    'cake': Item(
        emoji='🍰',
        name='cake',
        ru_name='Торт',
        cost=500,
        type='food'
    ),


    'sake': Item(
        emoji='🍶',
        name='sake',
        ru_name='Саке',
        cost=100,
        type='food'
    ),


    'pita': Item(
        emoji='🥙',
        name='pita',
        ru_name='Пита Сэндвич',
        cost=200,
        type='food'
    ),


    'red_car': Item(
        emoji='🚗',
        name='red_car',
        ru_name='Красная машина',
        cost=10000,
        type='car'
    ),


    'blue_car': Item(
        emoji='🚙',
        name='blue_car',
        ru_name='Синяя машина',
        cost=15000,
        type='car'
    ),


    'racing_car': Item(
        emoji='🏎️',
        name='racing_car',
        ru_name='Гоночный автомобиль',
        cost=40000,
        type='car'
    ),


    'clown': Item(
        emoji='🤡',
        name='clown',
        ru_name='Клоун',
        cost=100,
        type='mask'
    ),


    'ghost': Item(
        emoji='👻',
        name='ghost',
        ru_name='Призрак',
        cost=100,
        type='mask'
    ),


    'alien': Item(
        emoji='👽',
        name='alien',
        ru_name='Пришелец',
        cost=100,
        type='mask'
    ),


    'robot': Item(
        emoji='🤖',
        name='robot',
        ru_name='Робот',
        cost=100,
        type='mask'
    ),


    'shit': Item(
        emoji='💩',
        name='shit',
        ru_name='Какашка',
        cost=100,
        type='mask'
    ),


    'fondue': Item(
        emoji='🫕',
        name='fondue',
        ru_name='Фондю',
        cost=100,
        type='food'
    ),


    'juice': Item(
        emoji='🥤',
        name='juice',
        ru_name='Сок',
        cost=100,
        type='food'
    ),


    'cactus': Item(
        emoji='🌵',
        name='cactus',
        ru_name='Кактус',
        cost=250,
        type='mask'
    ),


    'palm': Item(
        emoji='🌴',
        name='palm',
        ru_name='Пальма',
        cost=345,
        type='mask'
    ),


    'potted_plant': Item(
        emoji='🪴',
        name='potted_plant',
        ru_name='Комнатное растение',
        cost=55,
        type='mask'
    ),


    'clover': Item(
        emoji='🍀',
        name='clover',
        ru_name='Клевер',
        cost=55,
        type='mask'
    ),


    'tulip': Item(
        emoji='🌷',
        name='tulip',
        ru_name='Тюльпан',
        cost=99,
        type='mask'
    ),


    'rose': Item(
        emoji='🌹',
        name='rose',
        ru_name='Роза',
        cost=123,
        type='mask'
    ),


    'xmas_tree': Item(
        emoji='🎄',
        name='xmas_tree',
        ru_name='Новогодняя елка',
        cost=123,
        type='mask'
    ),


    'moyai': Item(
        emoji='🗿',
        name='moyai',
        ru_name='Моаи',
        cost=123,
        type='mask'
    ),


    'chocolate': Item(
        emoji='🍫',
        name='chocolate',
        ru_name='Плитка шоколада',
        cost=321,
        type='food'
    ),


    'stethoscope': Item(
        emoji='🩺',
        name='stethoscope',
        ru_name='Стетоскоп',
        cost=444,
        type='mask'
    ),


    'metro': Item(
        emoji='🚇',
        name='metro',
        ru_name='Metro',
        cost=10,
        type='token'
    ),


    'traintoken': Item(
        emoji='🎫',
        name='traintoken',
        ru_name='Train',
        cost=10,
        type='token'
    ),


    'phone': Item(
        emoji='📱',
        name='phone',
        ru_name='Phone',
        cost=1000000,
        type='phone'
    ),


    'trolleytoken': Item(
        emoji='🧾',
        name='trolleytoken',
        ru_name='Trolley',
        cost=10,
        type='token'
    ),


    'hamster': Item(
        emoji='🐹',
        name='hamster',
        ru_name='Hamster',
        cost=100,
        type='mask'
    ),

    "fyCoin": Item(
        name="fyCoin",
        ru_name="fyCoin",
        emoji="💎",
        cost=-1,
        type="crypto"
    ),

    "Mithereum": Item(
        name="Mithereum",
        ru_name="Mithereum",
        emoji="🧿",
        cost=-1,
        type="crypto"
    ),

    "Gather": Item(
        name="Gather",
        ru_name="Gather",
        emoji="🧬",
        cost=-1,
        type="crypto"
    ),

    "Recegon": Item(
        name="Recegon",
        ru_name="Recegon",
        emoji="🪙",
        cost=-1,
        type="crypto"
    ),
}
'''Store all items in Jivopolis'''
