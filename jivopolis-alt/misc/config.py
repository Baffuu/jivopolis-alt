TOKEN = '6013919640:AAHd1ShmwsLvcM1x8HYiQaDNGJxZcehsOhQ'  #токен бота
ADMINS = [1006534370, 1002930622, 1196315173, 118198979]

MEGACHATLINK = 't.me/'
BAFFUADM = 't.me/'

# линии метро
METRO = [
            [   
                'Площадь Админов', 'Восток', 'Поречье', 'Микитская улица',
                'Александровская', 'Ботаническая', 'Парк Победы', 'Университет',
                'Котайский проспект', 'Старый город', 'Котаево', 'Зоопарк',
                'Котайский электрозавод', 'Ратуша', 'Михайлово', 'Крайний Юг', 'Никитино',
                'Даниловская', 'Агзамовщина', 'Историческая'
            ],
            [
                'Котайский Мединститут', 'Улица 8 Марта', 'Аэропорт Котай',
                'Александровская', 'Георгиевская', 'Живбанк', 'Первоапрельская',
                'Автопарк им. Кота', 'Вокзальная', 'ТЦ МиГ', 'Генерала Шелби',
                'Юго-Западная', 'Историческая', 'Кольцевая', 'Генерала Шелби'
            ],
            [
                'Крайний Север', 'Площадь Админов', 'Ракенская', 'Райбольница',
                'Живополисский музей', 'Тропическая', 'Живополис-Восточный',
                'Роща', 'Вокзальная', 'Автовокзал Живополис', 'Живополис-Южный',
                'Старый город', 'Котай-Главный', 'Мясокомбинат', 'Котай-Западный',
                'Максименка', 'Переулок Феликса', 'Улица 8 Марта', 'Северянка',
                'Крайний Север'
            ],
            [
                'Северо-Восток', 'Аэродромная', 'Полночь', 'Райбольница',
                'Котянка', 'Макеевка', 'Георгиевская', 'Ботаническая',
                'Автозаводская', 'Максименка', 'Западница', 'Мясокомбинат',
                'Университет', 'Стадион', 'Победа', 'Ботаническая'
            ]
        ]

#маршрут троллейбуса
CITY = \
    [
        'Площадь Админов', 'Восток', 'Поречье', 'Река Олёнка', 'Микитская улица',
        'АС Александрово', 'Александровская', 'Ботаническая', 'Парк Победы',
        'Университет', 'Котайский проспект', 'Старый город', 'Старово', 'Котаево',
        'Зоопарк', 'Котайский электрозавод', 'Ратуша', 'Михайлово', 'Крайний Юг',
        'Никитино', 'Даниловская', 'Агзамовщина', 'Историческая',
        'Котайский Мединститут', 'Улица 8 Марта', 'Аэропорт Котай',
        'Географический центр', 'Улица Центральная', 'Георгиевская', 'Живбанк',
        'Первоапрельская', '3-й микрорайон', 'Автопарк им. Кота', 'Вокзальная',
        'ТЦ МиГ', 'Генерала Шелби', 'Юго-Западная', 'Улица Кодовая', 'Кольцевая',
        'Крайний Север', 'Ракенская', 'Райбольница', 'Живополисский музей',
        'Тропическая', 'Живополис-Восточный', 'Роща', 'Автовокзал Живополис',
        'Улица Лесная', 'Живополис-Южный', 'Станция Котай', 'Котай-Главный',
        'Мясокомбинат', 'Котай-Западный', 'Максименка-Западница', 'Максименка',
        'Переулок Феликса', 'Улица 8 Марта', 'Северянка', 'Северо-Восток',
        'Аэродромная', 'Национальный аэропорт', 'Полночь', 'Райбольница', '7-й км',
        'Котянка', 'Макеевка', '18-й км', 'Автозаводская', 'Западница', 'Стадион',
        'Победа', 'Улица Спортивная', 'пос. Красный'
    ]

#маршрут автобуса
villages = \
    [
        'Автовокзал Живополис', 'АС Александрово', 'Красный',
        'Максименка-Западница', 'Глубинка', 'Цель', '18-й км', 'Старокотай',
        'Микитай', 'Загорье', 'Попережье', 'Деревцы'
    ]

#лотерейные призы
PRIZES = \
    [
        'morj', 0, 10, 10, 10, 100, 3, 14, 90, 5, 1000, 10, 3, 3, 3, 5, 5, 0, 10,
        5, 0, 0, 10, 5, 3, 3, 5, 5, 10, 14, 14, 14, 5, 5, 10, 5, 0, 'cow', -5, -10,
        0, 5, 10
    ]

ID = 2055111795  #айди бота

SUPPORT_LINK = 't.me/'

banned = []  #пользователи в бане

WALK = \
    [ ##список мест, в которые можно добраться пешком
        [
            'Национальный аэропорт', 'Станция Котай', 'АС Александрово',
            'Площадь Админов', 'Старокотай', 'Красный',
        ],
        [
            'Аэродромная', 'Котай-Главный', 'Александровская', 'Рынок',
            'Старокотайский ФАП', 'пос. Красный',
        ],
        [
            '', '', '', 'Админская улица', '', ''
        ],
    ] 


walks = [45, 60, 90, 45, 75, 60]  #продолжительность ходьбы #todo insert into walk
limeteds = ['baguette', 'tea', 'pita', 'pelmeni', 'meat_on_bone']  #дефицитные товары #todo rename

market = []

clanitems = \
    [
        [ ##предметы, доступные для покупки в кланах
            'medicine', 'kisel', 'porridge'
        ], 
        [ ##стоимость предметов в кланах
            400, 20, 20
        ]
    ]

traincost = 30  #стоимость билета на поезд
metrocost = 20  #стоимость жетона метро
trolleycost = 15  #стоимость проездного талона
aircost = 75  #стоимость полёта на самолёте
buscost = 100  #стоимость поездки на маршрутке
regbuscost = 50  #стоимость поездки на междугородном автобусе
fightlim = 60  #кулдаун при битвах
ticket_time = 720  #время, через которое сообщение

#интервалы и продолжительность посадки на разные ТС (в секундах)
intervals = \
    {
        'metro': [300, 60], #интервал движения поездов метро
        'trolleybus': [600, 120], #интервал движения городских троллейбусов
        'train': [1200, 240], #интервал движения поездов региональных линий
        'bus': [1200, 300], #интервал движения междугородных автобусов
        'plane': [3600, 1800],  #интервал движения самолётов
        'taxi': [900, 90], #интервал движения пригородных маршрутных такси
        'citylines': [600, 60],  #интервал движения поездов городских линий
    }  

#сообщения, появляющиеся по команде /start
randomtext = [
    'Мы все равны: и разумные существа, и жабы', 'Время валить отсюда',
    'Опять цены на проезд повысили :(', 'лёгушька', 'Слава Василию!',
    'В главных ролях', 'Слава Миките', 'Где можно купить немного денег?',
    'А сейчас мы с вами наблюдаем жабу - самое беспомощное и бессмысленное существо во Вселенной',
    'Типичное состояние жителя Живополиса - <b>$0</b>',
    'У нас закончилось всё... И деньги в том числе',
    'Чтобы прокатиться на метро, нажмите "Город"',
    'Ехал жаба через жаба\nВидит жаба - в жабе жаба\nСунул жаба лапу в жаба\nЖабу жаба <b>____</b>\n<b>Вывод:</b> не будьте жабой',
    '<code>слава миките слава миките слава миките</code>\nЧто делать с этим текстом, решайте сами',
    'Обычно этот текст не читают',
    'Квадрат гипотенузы равен сумме квадратов катетов',
    'Пока еноты у власти Живополиса наедаются макаронами, простые смертные вынуждены есть хлеб, которого в магазинах уже нет(',
    'I like to move it, move it',
    'Сколько раз за этот месяц повышали цены на еду? Так жить нельзя',
    'И запомните, дети: Микита - самый некоррумпированный император за всю историю человечества',
    'Еноты - и точка', 'No zhabas', 'почему', 'Наконец-то с инлайн-режимом', 
    'вентигурелятор 3000 - новый вентилятор регулирующий ваш баланс. С таким больше 3000 вы никогда не наберёте! ещё и вентилятор в подарок',
    '👁👄👁', 'ходят слухи, что админы живополиса гнобят жаб…',
]

#айди канала состояния бота
botstate = -1001564276460

#приветствия по команде /start
hellos = [
    'Привет', 'Здравия желаю', 'Добро пожаловать',
    'Добро пожаловать в Живополис', 'Здравствуйте', 'Приветствую',
    'Приветствуем', 'С днём енота', 'Как дела', 'Как поживаешь'
]

#еда
FOOD = [
    [
        'bread', 'milk', 'soup', 'pelmeni', 'apple', 'shaurma', 'burger', 'pizza',
        'cocoa', 'kiwi', 'tomato', 'fries', 'cucumber', 'pasta', 'donut', 'sushi',
        'beer', 'meat', 'cheburek', 'tea', 'rice', 'cookie', 'cake', 'yogurt',
        'meatcake', 'porridge', 'kisel', 'chocolate', 'icecream', 'fruitice'
    ], 
    [
        3, 15, 10, 7, 5, 1000, 1000, 900, 20, 10, 5, 900, 5, 5, 5, 20, 5, 5, 900,
        5, 10, 5, 10, 5, 7, 5, 5, 7, 10, 7
    ], []]

#насыщение от разных видов еды

#опыт для уровней
levelrange = [
    0, 1, 5, 10, 20, 30, 45, 70, 100, 140, 200, 250, 310, 380, 450, 520, 610,
    700, 800, 910, 1030, 1050, 1100, 1200, 1320, 1500, 1750, 2000, 2100, 2250,
    2500, 2750, 3000, 3500, 4000, 4500, 5000, 5750, 6500, 7500, 8500, 10000,
    12500
]
#описания уровней
leveldesc = [
    '', '', '', '', '<b>Доступные функции:</b>\n&#128661; Поездка на такси',
    '<b>Доступные функции:</b>\n&#128275; Создание публичного клана', '', '',
    '<b>Доступные предметы:</b>\n&#128663; Красный автомобиль\n&#128665; Синий автомобиль',
    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''
]

lvlclan = 5  #минимальный уровень для создания публичного клана
lvlcab = 4  #минимальный уровень для поездки на такси
cabcost = 5  #минимальная стоимость поездки на такси

#линии метро в именительном падеже
LINES = [
    'Восточная линия городской электрички', 'Первоапрельская линия',
    'Кольцевая линия городской электрички', 'Электрозаводская линия'
]
#линии метро в родительном падеже
linez = [
    'Восточной линии городской электрички', 'Первоапрельской линии',
    'Кольцевой линии городской электрички', 'Электрозаводской линии'
]
#страны и столицы для Географии в университете
countries = [
    '🇰🇵 КНДР', '🇫🇮 Финляндия', '🇩🇰 Дания', '🇳🇴 Норвегия', '🇸🇪 Швеция',
    '🇨🇭 Швейцария', '🇮🇸 Исландия', '🇹🇷 Турция', '🇧🇾 Республика Беларусь',
    '🇨🇳 Китайская Народная Республика', '🇰🇷 Республика Корея', '🇰🇿 Казахстан',
    '🇮🇱 Израиль', '🇨🇾 Кипр', '🇧🇷 Бразилия', '🇷🇺 Российская Федерация',
    '🇺🇦 Украина', '🇩🇪 ФРГ', '🇫🇷 Франция', '🇯🇵 Япония', '🇦🇩 Андорра',
    '🇱🇰 Шри-Ланка', '🇷🇸 Сербия', '🇱🇮 Лихтенштейн', '🇹🇩 Чад', '🇺🇿 Узбекистан',
    '🇦🇷 Аргентина', '🇪🇨 Эквадор', '🇮🇹 Италия', '🇪🇸 Испания', '🇵🇹 Португалия',
    '🇮🇪 Ирландия', '🇬🇧 Соединённое Королевство', '🇹🇲 Туркмения', '🇺🇬 Уганда',
    '🇧🇬 Болгария', '🇭🇷 Хорватия', '🇲🇪 Черногория', '🇮🇷 Иран', '🇹🇿 Танзания',
    '🇨🇲 Камерун', '🇧🇫 Буркина-Фасо', '🇲🇳 Монголия', '🇸🇱 Сьерра-Леоне',
    '🇬🇳 Гвинея', '🇬🇼 Гвинея-Бисау', '🇪🇬 Египет', '🇿🇦 ЮАР', '🇳🇿 Новая Зеландия',
    '🇦🇺 Австралия', '🇬🇷 Греция', '🇧🇳 Бруней', '🇲🇾 Малайзия', '🇱🇸 Лесото',
    '🇰🇬 Кыргызстан'
]
capitals = [
    'Пхеньян', 'Хельсинки', 'Копенгаген', 'Осло', 'Стокгольм', 'Берн',
    'Рейкьявик', 'Анкара', 'Минск', 'Пекин', 'Сеул', 'Нур-Султан', 'Иерусалим',
    'Никосия', 'Бразилиа', 'Москва', 'Киев', 'Берлин', 'Париж', 'Токио',
    'Андорра-ла-Велья', 'Шри-Джаяварденепура-Котте', 'Белград', 'Вадуц',
    'Нджамена', 'Ташкент', 'Буэнос-Айрес', 'Кито', 'Рим', 'Мадрид', 'Лиссабон',
    'Дублин', 'Лондон', 'Ашхабад', 'Кампала', 'София', 'Загреб', 'Подгорица',
    'Тегеран', 'Додома', 'Яунде', 'Уагадугу', 'Улан-Батор', 'Фритаун',
    'Конакри', 'Бисау', 'Каир', 'Претория', 'Веллингтон', 'Канберра', 'Афины',
    'Бандар-Сери-Бегаван', 'Куала-Лумпур', 'Масеру', 'Бишкек'
]
ach = [[], [], [], [], [], [], [], []]

ACHIEVEMENTS = \
    {   #achievement: name, description, [reward: money, XP], db slot
        'first_jackpot': [''],
        'masquerade': ['&#128122; Маскарад', 'Наденьте любую маску', [10, 4], 'masquerade'],
    }
#достижения
ach[0] = [
    'jkp', 'lucky', 'firstwin', 'myauto', 'helper', 'black', 'medquest',
    'busride', 'flightach', 'walkach', 'soldach', 'cabach'
]
#названия достижений
ach[1] = [
    '&#127808; Удача в придачу', '&#127920; Профессиональный игрок',
    '&#9876; Первая победа', '&#128663; Личное авто', '&#128138; Спасатель',
    '&#129689; На другой стороне', '&#129658; Клятва Гиппократа',
    '&#128652; Вдалеке от цивилизации', '&#128745; Полёт нормальный',
    '&#128694; Лучший вид транспорта', '&#128178; Барыга', '&#128661; Дорого-богато'
]
#описания достижений
ach[2] = [
    'Поймайте джекпот, играя в Игровом клубе', '10 раз поймайте джекпот, играя в Игровом клубе',
    'Победите кого-нибудь в поединке. Чтобы начать бой, напишите <code>бой</code> в ответ на любое сообщение соперника',
    'Купите любой автомобиль в Автопарке', 'Воскресите умершего игрока',
    'Зайдите на Чёрный рынок',
    'Вылечите 20 игроков от травмы или смерти, используя Лекарства',
    'Свалите на маршрутке в любую деревню через Автовокзал',
    'Полетайте на самолёте', '20 раз походите пешком',
    '10 раз продайте любой товар на Центральном рынке', 'Проедьте на такси от самой первой в списке до самой последней местности'
]
#награда за достижения (деньги)
ach[3] = [10, 50, 200, 10, 100, 50, 100, 150, 150, 100, 100, 150, 150]
#награда за достижения (опыт)
ach[4] = [4, 10, 25, 5, 10, 10, 15, 20, 20, 15, 10, 20, 15]
#столбцы, показывающие степень выполнения достижений
ach[5] = [
    'jkp', 'jackpots', 'firstwin', 'myauto', 'helper', 'black', 'cured',
    'busride', 'flightach', 'walk', 'sold', 'cabach'
]
#максимальная степень выполнения достижений
ach[6] = [1, 1, 10, 1, 1, 1, 1, 20, 1, 1, 20, 10, 1]
#категории достижений
ach[7] = ['Игровой процесс', 'Нелегальные занятия', 'Нелегальные занятия', 'Игровой процесс', 'Игровой процесс',  'Помощь игрокам',  'Нелегальные занятия', 'Помощь игрокам', 'Путешествия', 'Путешествия', 'Путешествия', 'Игровой процесс', 'Путешествия']
locations = [
    [
        '🏬 ТЦ МиГ', '🍰 СладкоЁжка', '🍏 Натурал', '🏣 Рынок', '🦊 Зоопарк',
        '🌲 Ботанический сад', '📱 Магазин техники', '🚗 Автопарк', '🏭 Электрозавод',
        '🏫 Университет', '🌾 Ферма', '🏥 Райбольница', '🏥 Старокотайский ФАП',
        '✈ Нац. аэропорт', '✈ Аэропорт Котай', '🚆 Центральный вокзал',
        '🚆 Александровский вокзал', '🚆 Котайский вокзал', '🚌 АВ Живополис',
        '🚌 АС Александрово', '🏦 Живбанк', '🏟 Живополис-Арена'
    ],
    [
        'Крупный торговый центр. Магазины:\n👚 ModaShop\n🍚 Ресторан японской кухни "Япон Енот"\n🍔 Енот Кебаб',
        'Кондитерская с очень вкусной едой', 'Магазин с фруктами и овощами',
        'Вам нужно сюда, если у вас есть ненужная еда или маски, которые вы хотите продать',
        'Магазин масок в виде животных', 'Магазин "цветочных" масок',
        'Магазин электронных устройств', 'Лучшие автомобили Живополиса!',
        'Место для заработка денег с помощью мини-игр',
        'Здесь можно получить опыт, играя в мини-игры',
        'Здесь можно подоить корову и получить молоко',
        'Здесь можно купить таблетки',
        'Быстрый доступ к таблеткам для деревенских жителей',
        'Аэровокзал города Живополис', 'Аэровокзал города Котай',
        'Железнодорожный вокзал города Живополис',
        'Железнодорожный вокзал городка Александрово',
        'Железнодорожный вокзал города Котай', 'Автовокзал города Живополис',
        'Небольшой автовокзальчик городка Александрово',
        'Крупнейший банк Живополиса, который можно ограбить :)',
        'Основной турнирный стадион Живополиса'
        ], [], []]
#названия локаций

#описания локаций

#местности локаций
locations[2] = [
    'ТЦ МиГ', 'Георгиевская', 'Макеевка', 'Рынок', 'Зоопарк', 'Ботаническая',
    'Генерала Шелби', 'Автопарк им. Кота', 'Котайский электрозавод',
    'Университет', 'Роща', 'Райбольница', 'Старокотайский ФАП',
    'Национальный аэропорт', 'Аэропорт Котай', 'Вокзальная', 'Александровская',
    'Станция Котай', 'Автовокзал Живополис', 'АС Александрово', 'Живбанк',
    'Стадион'
]
#категории локаций
locations[3] = [
    'Торговля', 'Торговля', 'Торговля', 'Торговля', 'Торговля', 'Торговля',
    'Торговля', 'Торговля', 'Заработок', 'Заработок', 'Заработок', 'Здоровье',
    'Здоровье', 'Транспорт', 'Транспорт', 'Транспорт', 'Транспорт',
    'Транспорт', 'Транспорт', 'Транспорт', 'Прочее', 'Прочее'
]

trains = \
    [
        [ ##местности с о.п. поезда
            'Вокзальная', 'Александровская', 'Национальный аэропорт', 'Макеевка',
            'Роща', 'Станция Котай',
        ], 
        [ ##короткие названия о.п.
            'Живополис', 'Александрово', 'Национальный аэропорт',
            'Макеевка', 'Роща', 'Котай',
        ], 
        [ ##полные названия о.п.
            'Живополис-Пассажирский', 'Александрово',
            'Национальный аэропорт Живополис', 'Деревня Макеевка', 'Роща',
            'Котай-Пассажирский'
        ],
    ]