from dataclasses import dataclass
from typing import Literal, Union, Optional
ITEMS = {
        ## name: [icon, database slot name, name, cost, category, description, html-code of item's icon]
        'party_popper': ['🎉', 'party_popper', 'Хлопушка', 50, ['mask']],
        'mrs_claus': ['🤶', 'mrs_claus', 'Миссис Клаус', 75, ['mask']],
        'santa_claus': ['🎅', 'santa_claus', 'Санта Клaус', 100, ['mask']],
        'fairy': ['🧚', 'fairy', 'Фея', 50, ['mask']],
        'snowflake': ['❄️', 'snowflake', 'Снежинка', 30, ['mask']],
        'snowman': ['☃️', 'snowman', 'Снеговик', 50, ['mask']],
        'hedgehog': ['🦔', 'hedgehog', 'Еж', 100, ['mask']],
        'truck': ['🚚', 'truck', 'Грузовик', 3000, ['mask']],
        'gold_medal': ['🥇', 'gold_medal', 'Золотая медаль', -1, ['mask']],
        'silver_medal': ['🥈', 'silver_medal', 'Серебренная медаль', -1, ['mask']],
        'bronze_medal': ['🥉', 'bronze_medal', 'Бронзовая медаль', -1, ['mask']],
        'poison': ['🧪', 'poison', 'Яд', 4000, ['robber']],
        'baguette': ['🥖', 'baguette', 'Багет', 25, ['food']],
        'milk': ['🥛', 'milk', 'Молоко', 25, ['food']],
        'ramen': ['🍜', 'ramen', 'Рамен', 25, ['food']],
        'pelmeni': ['🍲', 'pelmeni', 'Пельмени', 50, ['food']],
        'apple': ['🍎', 'apple', 'Яблоко', 50, ['food']],
        'shawarma': ['🌯', 'shawarma', 'Шаурма', 25, ['food']],
        'burger': ['🍔', 'burger', 'Бургер', 500, ['food']],
        'pizza': ['🍕', 'pizza', 'Пицца', 200, ['food']],
        'coconut': ['🥥', 'coconut', 'Кокос', 25, ['food']],
        'kiwi': ['🥝', 'kiwi', 'Kиви', 10, ['food']],
        'tomato': ['🍅', 'tomato', 'Помидор', 10, ['food']], 
        'fries': ['🍟', 'fries', 'Картофель Фри', 10, ['food']],
        'cucumber': ['🥒', 'cucumber', 'Огурец', 10, ['food']],
        'spaghetti':['🍝', 'spaghetti', 'Спагетти', 10, ['food']],
        'doughnut': ['🍩', 'doughnut', 'Пончик', 10, ['food']],
        'bento': ['🍱', 'bento', 'Бенто', 500, ['food']],
        'beer': ['🍺', 'beer', 'Пиво', 200, ['food']],
        'meat_on_bone': ['🍖', 'meat_on_bone', 'Мясо на кости', 200, ['food']],
        'cheburek': ['🥟', 'cheburek', 'Чeбурек', 50, ['food']],
        'tea': ['🍵', 'tea', 'Чай', 50, ['food']],
        'coffee': ['☕', 'coffee', 'Кофе', 50, ['food']],
        'rice': ['🍚', 'rice', 'Рис', 70, ['food']],
        'cookie': ['🍪', 'cookie', 'Печенье', 20, ['food', 20], 'cookie'],
        'cake': ['🍰', 'cake', 'Торт', 500, ['food']],
        'sake': ['🍶', 'sake', 'Саке', 100, ['food']],
        'pita': ['🥙', 'pita', 'Пита Сэндвич', 200, ['food']],
        'red_car': ['🚗', 'red_car', 'Красная машина', 10000, ['car', 1]],
        'blue_car': ['🚙', 'blue_car', 'Синяя машина', 15000, ['car', 2]],
        'racing_car': ['🏎️', 'racing_car', 'Гоночный автомобиль', 40000, ['car', 5]],
        'clown': ['🤡', 'clown', 'Клоун', 100, ['mask']],
        'ghost': ['👻', 'ghost', 'Призрак', 100, ['mask']],
        'alien': ['👽', 'alien', 'Пришелец', 100, ['mask']],
        'robot': ['🤖', 'robot', 'Робот', 100, ['mask']],
        'shit': ['💩', 'shit', 'Какашка', 100, ['mask']],
        'fondue': ['🫕', 'fondue', 'Фондю', 100, ['food', 100]],
        'juice': ['🥤', 'juice', 'Сок', 100, ['food']],
        'cactus': ['🌵', 'cactus', 'Кактус', 250, ['mask']],
        'palm': ['🌴', 'palm', 'Пальма', 345, ['mask']],
        'potted_plant': ['🪴', 'potted_plant', 'Комнатное растение', 55, ['mask']],
        'clover': ['🍀', 'clover', 'Клевер', 55, ['mask']],
        'tulip': ['🌷', 'tulip', 'Тюльпан', 99, ['mask']],
        'rose': ['🌹', 'rose', 'Роза', 123, ['mask']],
        'xmas_tree': ['🎄', 'xmas_tree', 'Новогодняя елка', 123, ['mask']],
        'moyai': ['🗿', 'moyai', 'Моаи', 123, ['mask']],
        'chocolate': ['🍫', 'chocolate', 'Плитка шоколада', 321, ['food']],
        'shaved_ice': ['🍧', 'shaved_ice', 'Фруктовый лед', 41, ['food']],
        'ice_cream': ['🍨', 'ice_cream', 'Мороженое', 569, ['food']],
        'stethoscope': ['🩺', 'stethoscope', 'Стетоскоп', 444, ['mask']],
        'metro': ['🚇', 'metro', 'Metro', 10, ['token']],
        'traintoken': ['🎫', 'traintoken', 'Train', 10, ['token']],
        'phone': ['📱', 'phone', 'Phone', 1000000, ['phone']],
        'troleytoken': ['🧾', 'trolleytoken', 'Trolley', 10, ['token']],
        'hamster': ['🐹', 'hamster', 'Hamster', 100, ['mask']],
        'fox': ['🦊', 'fox', 'Лиса', 500, ['mask'], 'она украла текст. Теперь здесь нет ничего. Ну, кроме котиков, разумеется.\n🐈🐈🐈🐈 Коты захватили мир!!!'],

    }

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

allitems = {
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
    )

}