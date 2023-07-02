from dataclasses import dataclass
from typing import Literal, Union, Optional, Any


@dataclass
class Item():
    name: str
    ru_name: str
    emoji: Optional[str] = '🌀'
    cost: int = -1
    type: Optional[str] = None
    type_param: Optional[Union[str, int, list[Any]]] = None
    description: Optional[str] = None

    @property
    def price(self) -> Union[int, Literal['no cost']]:
        '''
        You can get cost (or price) of the item
        '''
        return (
            'no cost'
            if self.cost < 0
            or not self.cost
            else self.cost
        )


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
            description='очень старый ключ.'
                        'Кто знает, может быть, однажды он пригодится…'
    ),

    'gun': Item(
            name='gun',
            ru_name='Пистолет',
            emoji='🔫',
            type='robber',
            cost=1000,
            description='водный пистолет. Кажется, '
                        'его потерял какой-то ребёнок'
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
        description='древний китайский ниндзя, которому уже много-много лет'
                    '...\n\n**китайский Партия одобряет'
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
        description='поздравляем!'
    ),

    'pill': Item(
        name='pill',
        ru_name='Таблетка',
        emoji='💊',
        cost=500,
        type='medicine',
        description='принимайте, только если у вас есть рецепт от врача'
    ),

    'fireworks': Item(
        name='fireworks',
        ru_name="Фейерверки",
        emoji='🎆',
        cost=100,
        type='mask',
        description='удовольствие на пять минут, а стоят, как целый город'
    ),

    'party_pooper': Item(
        name='party_pooper',
        ru_name='Хлопушка',
        emoji='🎉',
        cost=50,
        type='mask',
        description='будьте аккуратны при использовании!'
    ),

    'window': Item(
        name='window',
        ru_name='Окно',
        emoji='🪟',
        cost=400,
        type='building_material',
        description='не выпрыгивать и не вылетать!'
    ),

    'brick': Item(
        name='brick',
        ru_name='Кирпич',
        emoji='🧱',
        cost=100,
        type='building_material',
        description='просто кирпич. Нужен для постройки дома'
    ),

    'door': Item(
        name='door',
        ru_name='Дверь',
        emoji='🚪',
        cost=500,
        description='тук-тук'
    ),

    'fox': Item(
        name='fox',
        ru_name='Лиса',
        emoji='🦊',
        cost=100,
        type='mask',
        description='лиса украла описание, поэтому тут ничего нет'
    ),

    'baguette': Item(
        name='baguette',
        ru_name='Багет',
        emoji='🥖',
        cost=25,
        type='food',
        description='ah, tu viens de France?'
    ),

    'apple': Item(
        name='apple',
        ru_name='Яблоко',
        emoji='🍎',
        cost=50,
        type='food',
        description='одна из причин массового увольнения врачей в Живополисе'
    ),

    'doughnut': Item(
        name='doughnut',
        ru_name='Пончик',
        emoji='🍩',
        cost=10,
        type='food',
        description='любимая еда американских полицейских'
    ),

    'fries': Item(
        name='fries',
        ru_name='Картофель Фри',
        emoji='🍟',
        cost=10,
        type='food',
        description='вопреки названию, к сожалению, платный'
    ),

    'ice_cream': Item(
        name='ice_cream',
        ru_name='Мороженое',
        emoji='🍨',
        cost=250,
        type='food',
        description='мозг замёрз...'
    ),

    'shaved_ice': Item(
        name='shaved_ice',
        ru_name='Фруктовый лед',
        emoji='🍧',
        cost=41,
        type='food',
        description='когда не хватает денег на обычное мороженое'
    ),

    'fairy': Item(
        name='fairy',
        ru_name='Фея',
        emoji='🧚',
        cost=-1,
        type='mask',
        description='сворует все ваши зубы'
    ),

    'kiwi': Item(
        name='kiwi',
        ru_name='Kиви',
        emoji='🥝',
        cost=10,
        type='food',
        description='птица или платёжный сервис?'
    ),

    'ramen': Item(
        name='ramen',
        ru_name='Рамен',
        emoji='🍜',
        cost=25,
        type='food',
        description='любимое блюдо живополисских студентов'
    ),

    'gold_medal': Item(
        name='gold_medal',
        ru_name='Золотая медаль',
        emoji='🥇',
        cost=-1,
        type='mask',
        description='она не золотая, а позолоченная :('
    ),

    'silver_medal': Item(
        name='silver_medal',
        ru_name='Серебряная медаль',
        emoji='🥈',
        cost=-1,
        type='mask',
        description='к сожалению, серебра в ней енот наплакал'
    ),

    'bronze_medal': Item(
        name='bronze_medal',
        ru_name='Бронзовая медаль',
        emoji='🥉',
        cost=-1,
        type='mask',
        description='прямиком из бронзового века'
    ),

    'mrs_claus': Item(
        emoji='🤶',
        name='mrs_claus',
        ru_name='Миссис Клаус',
        cost=75,
        type='mask',
        description='любит есть печенье, которое сама и готовит'
    ),

    'santa_claus': Item(
        emoji='🎅',
        name='santa_claus',
        ru_name='Санта Клaус',
        cost=100,
        type='mask',
        description='ты хорошо себя вёл в этом году?'
    ),

    'snowflake': Item(
        emoji='❄️',
        name='snowflake',
        ru_name='Снежинка',
        cost=30,
        type='mask',
        description='тает на ладони, как и надежды на счастливую жизнь '
                    'в Живополисе...'
    ),


    'snowman': Item(
        emoji='☃️',
        name='snowman',
        ru_name='Снеговик',
        cost=50,
        type='mask',
        description='главный враг детей на улице'
    ),


    'hedgehog': Item(
        emoji='🦔',
        name='hedgehog',
        ru_name='Ёж',
        cost=100,
        type='mask',
        description='ходячий кактус'
    ),


    'truck': Item(
        emoji='🚚',
        name='truck',
        ru_name='Грузовик',
        cost=3000,
        type='robber',
        description='ездить на нём, к сожалению, нельзя'
    ),


    'poison': Item(
        emoji='🧪',
        name='poison',
        ru_name='Яд',
        cost=4000,
        type='robber',
        description='содержится в любом блюде из Енот Кебаба. Ой'
    ),


    'milk': Item(
        emoji='🥛',
        name='milk',
        ru_name='Молоко',
        cost=25,
        type='food',
        description='натуральное, без ГМО'
    ),


    'pelmeni': Item(
        emoji='🍲',
        name='pelmeni',
        ru_name='Пельмени',
        cost=50,
        type='food',
        description='много мяса, мало теста'
    ),


    'shawarma': Item(
        emoji='🌯',
        name='shawarma',
        ru_name='Шаурма',
        cost=25,
        type='food',
        description='ешьте осторожнее...'
    ),


    'burger': Item(
        emoji='🍔',
        name='burger',
        ru_name='Бургер',
        cost=500,
        type='food',
        description='деликатес для студентов Котайского университета'
    ),


    'pizza': Item(
        emoji='🍕',
        name='pizza',
        ru_name='Пицца',
        cost=200,
        type='food',
        description='она же без ананасов, верно?'
    ),


    'coconut': Item(
        emoji='🥥',
        name='coconut',
        ru_name='Кокос',
        cost=25,
        type='food',
        description='больно бьёт по голове и по карману'
    ),


    'tomato': Item(
        emoji='🍅',
        name='tomato',
        ru_name='Помидор',
        cost=10,
        type='food',
        description='красный овощ... Или фрукт? Биологи из Котайского '
                    'университета утверждают, что помидоры - это млекопитающие'
    ),


    'cucumber': Item(
        emoji='🥒',
        name='cucumber',
        ru_name='Огурец',
        cost=10,
        type='food',
        description='не солёный'
    ),


    'spaghetti': Item(
        emoji='🍝',
        name='spaghetti',
        ru_name='Спагетти',
        cost=10,
        type='food',
        description='buonissimo!'
    ),


    'bento': Item(
        emoji='🍱',
        name='bento',
        ru_name='Бенто',
        cost=500,
        type='food',
        description='деликатес...'
    ),


    'beer': Item(
        emoji='🍺',
        name='beer',
        ru_name='Пиво',
        cost=200,
        type='food',
        description='сегодня пятница, а завтра выходной'
    ),


    'meat_on_bone': Item(
        emoji='🍖',
        name='meat_on_bone',
        ru_name='Мясо на кости',
        cost=200,
        type='food',
        description='немного обглодано собаками, но выбирать не приходится'
    ),


    'cheburek': Item(
        emoji='🥟',
        name='cheburek',
        ru_name='Чeбурек',
        cost=50,
        type='food',
        description='я бы такое не пробовал...'
    ),


    'tea': Item(
        emoji='🍵',
        name='tea',
        ru_name='Чай',
        cost=50,
        type='food',
        description='по мнению британских учёных, лучшее лекарство ото '
                    'всех болезней'
    ),


    'coffee': Item(
        emoji='☕',
        name='coffee',
        ru_name='Кофе',
        cost=50,
        type='food',
        description='не пейте перед сном!'
    ),


    'rice': Item(
        emoji='🍚',
        name='rice',
        ru_name='Рис',
        cost=70,
        type='food',
        description='при его сборе не использовалась никакая рабская сила'
    ),


    'cookie': Item(
        emoji='🍪',
        name='cookie',
        ru_name='Печенье',
        cost=20,
        type='food',
        description='вкусно...'
    ),


    'cake': Item(
        emoji='🍰',
        name='cake',
        ru_name='Торт',
        cost=500,
        type='food',
        description='раз в год можно себе позволить'
    ),


    'sake': Item(
        emoji='🍶',
        name='sake',
        ru_name='Саке',
        cost=100,
        type='food',
        description='распивать алкогольные напитки плохо!'
    ),


    'pita': Item(
        emoji='🥙',
        name='pita',
        ru_name='Пита Сэндвич',
        cost=200,
        type='food',
        description='мало кто знает, что это такое, но вроде бы оно съедобное'
    ),


    'red_car': Item(
        emoji='🚗',
        name='red_car',
        ru_name='Красная машина',
        cost=10000,
        type='car',
        description='врум-врум'
    ),


    'blue_car': Item(
        emoji='🚙',
        name='blue_car',
        ru_name='Синяя машина',
        cost=15000,
        type='car',
        description='отличается от красной только ценой'
    ),


    'racing_car': Item(
        emoji='🏎️',
        name='racing_car',
        ru_name='Гоночный автомобиль',
        cost=40000,
        type='car',
        description='стоит дороже, чем 1000 годовых зарплат типичного'
                    ' жителя Живополиса'
    ),


    'clown': Item(
        emoji='🤡',
        name='clown',
        ru_name='Клоун',
        cost=100,
        type='mask',
        description='кто как обзывается, тот сам так называется'
    ),


    'ghost': Item(
        emoji='👻',
        name='ghost',
        ru_name='Призрак',
        cost=100,
        type='mask',
        description='говорят, что их не существует'
    ),


    'alien': Item(
        emoji='👽',
        name='alien',
        ru_name='Пришелец',
        cost=100,
        type='mask',
        description='наверно, ему на своей планете живётся лучше,'
                    ' чем типичному жителю Живополиса'
    ),


    'robot': Item(
        emoji='🤖',
        name='robot',
        ru_name='Робот',
        cost=100,
        type='mask',
        description='говорят, что они когда-нибудь заменят людей. Но вам '
                    'волноваться нечего, поскольку ни один робот не'
                    ' согласится работать за такую маленькую зарплату'
    ),


    'shit': Item(
        emoji='💩',
        name='shit',
        ru_name='Какашка',
        cost=100,
        type='mask',
        description='кто вообще мог додуматься купить такую маску? '
                    'Вместе с ней нужно купить хороший освежитель воздуха'
    ),


    'fondue': Item(
        emoji='🫕',
        name='fondue',
        ru_name='Фондю',
        cost=100,
        type='food',
        description='оу, вы из Швейцарии?'
    ),


    'juice': Item(
        emoji='🥤',
        name='juice',
        ru_name='Сок',
        cost=100,
        type='food',
        description='не так дорого, но достаточно вкусно'
    ),


    'cactus': Item(
        emoji='🌵',
        name='cactus',
        ru_name='Кактус',
        cost=-1,
        type='mask',
        description='колется'
    ),


    'palm': Item(
        emoji='🌴',
        name='palm',
        ru_name='Пальма',
        cost=345,
        type='mask',
        description='представьте, что вы на Мальдивах'
    ),


    'potted_plant': Item(
        emoji='🪴',
        name='potted_plant',
        ru_name='Комнатное растение',
        cost=55,
        type='mask',
        description='вкусно пахнет...'
    ),


    'clover': Item(
        emoji='🍀',
        name='clover',
        ru_name='Клевер',
        cost=55,
        type='mask',
        description='вам сегодня везёт!'
    ),


    'tulip': Item(
        emoji='🌷',
        name='tulip',
        ru_name='Тюльпан',
        cost=99,
        type='mask',
        description='прямиком из Амстердама. Жаль, что это не столица '
                    'Нидерландов, а село в Живополисе'
    ),


    'rose': Item(
        emoji='🌹',
        name='rose',
        ru_name='Роза',
        cost=123,
        type='mask',
        description='романтично. Если только у вас нет на неё аллергии'
    ),


    'xmas_tree': Item(
        emoji='🎄',
        name='xmas_tree',
        ru_name='Новогодняя ёлка',
        cost=123,
        type='mask',
        description='раз, два, три, ёлочка, гори!'
    ),


    'moyai': Item(
        emoji='🗿',
        name='moyai',
        ru_name='Моаи',
        cost=123,
        type='mask',
        description='...'
    ),


    'chocolate': Item(
        emoji='🍫',
        name='chocolate',
        ru_name='Плитка шоколада',
        cost=321,
        type='food',
        description='много не ешьте, пожалуйста, а то у нас дефицит шоколада '
                    'и врачей'
    ),


    'stethoscope': Item(
        emoji='🩺',
        name='stethoscope',
        ru_name='Стетоскоп',
        cost=444,
        type='mask',
        description='что-то на медицинском'
    ),


    'metrotoken': Item(
        emoji='🚇',
        name='metrotoken',
        ru_name='Метрожетон',
        cost=25,
        type='token',
        description='лучший способ избежать пробок'
    ),


    'traintoken': Item(
        emoji='🎫',
        name='traintoken',
        ru_name='Билет на поезд',
        cost=75,
        type='token',
        description='чтобы уехать из Живополиса в поисках лучшей жизни'
    ),


    'regtraintoken': Item(
        emoji='🚆',
        name='regtraintoken',
        ru_name='Билет на электричку',
        cost=35,
        type='token',
        description='менее комфортный, зато более дешёвый способ свалить '
                    'навсегда из Живополиса'
    ),


    'phone': Item(
        emoji='📱',
        name='phone',
        ru_name='Смартфон',
        cost=800,
        type='phone',
        description='go touch some grass'
    ),


    'trolleytoken': Item(
        emoji='🚎',
        name='trolleytoken',
        ru_name='Билет на троллейбус',
        cost=30,
        type='token',
        description='зато экологично'
    ),


    'tramtoken': Item(
        emoji='🚋',
        name='trolleytoken',
        ru_name='Билет на трамвай',
        cost=45,
        type='token',
        description='я бы не советовал путешествовать на этом дряхлом '
                    'трамвае...'
    ),


    'hamster': Item(
        emoji='🐹',
        name='hamster',
        ru_name='Хомяк',
        cost=100,
        type='mask',
        description='милота... Надеюсь, он проживёт больше недели'
    ),

    "fyCoin": Item(
        name="fyCoin",
        ru_name="fyCoin",
        emoji="💎",
        cost=-1,
        type="crypto",
        description='видимо, единственный способ выжить на зарплату '
                    'рабочего в Живополисе'
    ),

    "Mithereum": Item(
        name="Mithereum",
        ru_name="Mithereum",
        emoji="🧿",
        cost=-1,
        type="crypto",
        description='возможно, это поможет вам разбогатеть'
    ),

    "Gather": Item(
        name="Gather",
        ru_name="Gather",
        emoji="🧬",
        cost=-1,
        type="crypto",
        description='вкладывайтесь с умом!'
    ),

    "Recegon": Item(
        name="Recegon",
        ru_name="Recegon",
        emoji="🪙",
        cost=-1,
        type="crypto",
        description='как же хорошо жить в XXI веке...'
    ),

    "fan": Item(
        name="fan",
        ru_name="Веep",
        emoji="🪭",
        cost=-1,
        type="mask",
        description='хорошая защита от жары. Наверное'
    )
}
'''Store all items in Jivopolis'''
