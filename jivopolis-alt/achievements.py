from dataclasses import dataclass


@dataclass
class Achievement():
    name: str
    ru_name: str
    description: str
    category: str

    # Achievement rewards.
    money_reward: int = 0
    xp_reward: int = 0

    # Special reward. Pass database column of the item.
    # Pass None for no special reward.
    special_reward: str | None = None

    # Database column for achievement progress.
    progress: str | None = None
    # Minimum progress for an achievement.
    completion_progress: int = 0


ACHIEVEMENTS = {
    'mask_achieve': Achievement(
        name='mask_achieve',
        ru_name='👺 Маскарад',
        description='Наденьте любую маску',
        category='👾 Игровой процесс',
        money_reward=25,
        xp_reward=5
    ),
    'auto_achieve': Achievement(
        name='auto_achieve',
        ru_name='🚗 Личное авто',
        description='Купите любой автомобиль в Автопарке',
        category='👾 Игровой процесс',
        money_reward=195,
        xp_reward=15
    ),
    'sell_achieve': Achievement(
        name='sell_achieve',
        ru_name='💲 Барыга',
        description='Продайте 10 любых товаров на Центральном рынке',
        category='👾 Игровой процесс',
        money_reward=100,
        xp_reward=10,
        progress="sell_progress",
        completion_progress=10
    ),
    'fish_achieve': Achievement(
        name='fish_achieve',
        ru_name='🐚 Охотник за сокровищами',
        description='Получите 3 ракушки в результате рыбалок. Рыбачить '
                    'можно в посёлке Морской',
        category='👾 Игровой процесс',
        money_reward=400,
        xp_reward=27,
        progress="fish_progress",
        completion_progress=3,
        special_reward="beaver"
    ),
    'proc_achieve': Achievement(
        name='proc_achieve',
        ru_name='🧙‍♂️ Философский камень',
        description='Превратите булыжник в золото с помощью завода в '
                    'местности Уголь',
        category='👾 Игровой процесс',
        money_reward=200,
        xp_reward=10
    ),
    'oscar_achieve': Achievement(
        name='oscar_achieve',
        ru_name='🏆 Дайте мне Оскар',
        description='Прокачайте свои отношения с Оскаром (владельцем лавки'
                    ' в Попережье) до уровня Топаз',
        category='👾 Игровой процесс',
        money_reward=200,
        xp_reward=17
    ),
    'luck_achieve': Achievement(
        name='luck_achieve',
        ru_name='🍀 Удача в придачу',
        description='Поймайте джекпот, играя в '
                    'казино в Игровом клубе',
        category='🎮 Развлечения',
        money_reward=50,
        xp_reward=7
    ),
    'jackpot_achieve': Achievement(
        name='jackpot_achieve',
        ru_name='🎰 Профессиональный игрок',
        description='10 раз поймайте джекпот, играя'
                    ' в казино в Игровом клубе',
        category='🎮 Развлечения',
        money_reward=500,
        xp_reward=32,
        progress='jackpot_progress',
        completion_progress=10,
        special_reward="key"
    ),
    'cab_achieve': Achievement(
        name='cab_achieve',
        ru_name='🚖 Дорого-богато',
        description='Прокатитесь на такси от самой первой'
                    ' местности до последней в списке или наоборот',
        category='🚖 Путешествия',
        money_reward=150,
        xp_reward=15
    ),
    'shuttle_achieve': Achievement(
        name='shuttle_achieve',
        ru_name='🚐 Вдалеке от цивилизации',
        description='Уедьте из города в любую деревню с '
                    'помощью Автовокзала Живополиса',
        category='🚖 Путешествия',
        money_reward=120,
        xp_reward=10
    ),
    'plane_achieve': Achievement(
        name='plane_achieve',
        ru_name='✈ 5 минут, полёт нормальный',
        description='Полетите куда-нибудь на самолёте',
        category='🚖 Путешествия',
        money_reward=200,
        xp_reward=17
    ),
    'tram_achieve': Achievement(
        name='tram_achieve',
        ru_name='🚋 Упс...',
        description='Попадите в аварию при попытке покататься '
                    'на трамвае в Ридиполе',
        category='🚖 Путешествия',
        money_reward=150,
        xp_reward=15
    ),
    'walk_achieve': Achievement(
        name='walk_achieve',
        ru_name='🚶‍♂️ На своих двоих',
        description='20 раз походите пешком',
        category='🚖 Путешествия',
        money_reward=100,
        xp_reward=10,
        progress='walk_progress',
        completion_progress=20
    ),
    'all_achieve': Achievement(
        name='all_achieve',
        ru_name='🏆 И это всё?',
        description='Получите все доступные на данный момент'
                    ' достижения (кроме этого, разумеется)',
        category='❌ Прочее',
        money_reward=1000,
        xp_reward=64,
        special_reward="parrot"
    )
}
'''Store all achievements available in Jivopolis'''
