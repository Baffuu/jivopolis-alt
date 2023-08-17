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

    # A special reward. Pass database column of the item or None if no special reward is given.
    special_reward: str | None = None

    # Database column for achievement progress and minimum progress for an achievement.
    progress: str | None = None
    completion_progress: int = 0


ACHIEVEMENTS = {

}
'''Store all achievements available in Jivopolis'''