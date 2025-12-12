"""Player Character subclass."""

from typing import Dict, Any
from src.models.characters.base import Character
from src.utils.constants import CHARACTER_TYPE_PC, STAT_MIN, STAT_MAX


class PC(Character):
    """
    Player Character class.
    
    Additional attributes for player-specific features like experience and
    stat point distribution.
    
    Attributes:
        experience: Experience points
        level: Character level (for future use)
    """
    
    def __init__(
        self,
        name: str,
        race: str,
        stat_points_to_distribute: int = 20,
    ):
        """
        Initialize a player character.
        
        Args:
            name: Character name
            race: Character race
            stat_points_to_distribute: Additional stat points to distribute (default 20)
        """
        super().__init__(
            name=name,
            race=race,
            character_type=CHARACTER_TYPE_PC,
            stat_points_to_distribute=stat_points_to_distribute,
        )
        self.experience = 0
        self.level = 1  # For future use
    
    def distribute_stat_points(self, points: int) -> None:
        """
        Distribute stat points to core stats.
        
        Args:
            points: Number of points to distribute
            
        Raises:
            ValueError: If points would exceed stat maximums
        """
        # This is a placeholder - actual implementation would allow player
        # to choose which stats to increase
        # For now, we'll just validate that points can be distributed
        
        if points < 0:
            raise ValueError("Points must be non-negative")
        
        # Check if there's room to distribute points
        total_current = sum(self.get_stat(stat) for stat in [
            "str", "constitution", "dex", "int", "wis", "luck"
        ])
        total_max = 6 * STAT_MAX
        
        if total_current + points > total_max:
            raise ValueError(f"Cannot distribute {points} points: would exceed maximum")
    
    def add_experience(self, amount: int) -> None:
        """
        Add experience points.
        
        Args:
            amount: Amount of experience to add
        """
        self.experience += amount
        # Future: level up logic would go here

