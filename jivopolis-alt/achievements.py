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
    'cab_achieve': Achievement(
        name='cab_achieve',
        ru_name='🚖 Дорого-богато',
        description='Прокатитесь на такси от самой первой'
                    ' местности до последней в списке',
        category='Путешествия',
        money_reward=150,
        xp_reward=15
    )
}
'''Store all achievements available in Jivopolis'''
