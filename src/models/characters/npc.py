"""NPC (Non-Player Character) subclass."""

from typing import Dict, Any, Optional
from src.models.characters.base import Character
from src.utils.constants import CHARACTER_TYPE_NPC


class NPC(Character):
    """
    NPC (Non-Player Character) class.
    
    Additional attributes for NPC-specific features like AI behavior.
    
    Attributes:
        ai_type: Type of AI behavior
        aggression_level: Aggression level (0.0 to 1.0)
    """
    
    def __init__(
        self,
        name: str,
        race: str,
        ai_type: str = "passive",
        aggression_level: float = 0.0,
        stat_points_to_distribute: int = 0,
    ):
        """
        Initialize an NPC.
        
        Args:
            name: Character name
            race: Character race
            ai_type: Type of AI behavior
            aggression_level: Aggression level (0.0 to 1.0)
            stat_points_to_distribute: Additional stat points (default 0 for NPCs)
        """
        super().__init__(
            name=name,
            race=race,
            character_type=CHARACTER_TYPE_NPC,
            stat_points_to_distribute=stat_points_to_distribute,
        )
        self.ai_type = ai_type
        
        if not 0.0 <= aggression_level <= 1.0:
            raise ValueError("aggression_level must be between 0.0 and 1.0")
        self.aggression_level = aggression_level
    
    def get_behavior_context(self) -> Dict[str, Any]:
        """
        Get context for AI behavior decisions.
        
        Returns:
            Dictionary containing behavior context information
        """
        return {
            "ai_type": self.ai_type,
            "aggression_level": self.aggression_level,
            "stats": {
                "str": self.get_stat("str"),
                "dex": self.get_stat("dex"),
                "int": self.get_stat("int"),
                "wis": self.get_stat("wis"),
            },
            "health_status": "unknown",  # Placeholder
            "threat_level": "unknown",  # Placeholder
        }

