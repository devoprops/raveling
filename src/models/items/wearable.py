"""Wearable equipment class."""

from typing import Dict, Any, Optional
from src.models.items.base import Item
from src.utils.constants import ITEM_TYPE_WEARABLE, EQUIPMENT_SLOTS


class Wearable(Item):
    """
    Wearable equipment that can be equipped to affect defense, stats, or skills.
    
    Attributes:
        defense_bonus: Bonus to defense value
        stat_boosts: Dictionary mapping stat names to boost values
        skill_boosts: Dictionary mapping skill names to boost values
        slot: Equipment slot this item occupies
    """
    
    def __init__(
        self,
        name: str,
        short_desc: str,
        long_desc: str,
        weight: float,
        size: float,
        material: str,
        slot: str,
        defense_bonus: float = 0.0,
        stat_boosts: Optional[Dict[str, float]] = None,
        skill_boosts: Optional[Dict[str, float]] = None,
        restrictions: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a wearable item.
        
        Args:
            name: Item name
            short_desc: Short description
            long_desc: Long description
            weight: Weight of the item
            size: Size of the item
            material: Material the item is made from
            slot: Equipment slot (must be in EQUIPMENT_SLOTS)
            defense_bonus: Bonus to defense
            stat_boosts: Dictionary of stat name -> boost value
            skill_boosts: Dictionary of skill name -> boost value
            restrictions: Optional dictionary of restrictions
        """
        super().__init__(
            name=name,
            short_desc=short_desc,
            long_desc=long_desc,
            item_type=ITEM_TYPE_WEARABLE,
            weight=weight,
            size=size,
            material=material,
            restrictions=restrictions,
        )
        
        if slot not in EQUIPMENT_SLOTS:
            raise ValueError(f"Invalid slot: {slot}. Must be one of {EQUIPMENT_SLOTS}")
        self.slot = slot
        
        self.defense_bonus = defense_bonus
        self.stat_boosts = stat_boosts or {}
        self.skill_boosts = skill_boosts or {}
    
    def get_defense_bonus(self) -> float:
        """
        Get the defense bonus provided by this item.
        
        Returns:
            Defense bonus value
        """
        return self.defense_bonus
    
    def get_stat_boosts(self) -> Dict[str, float]:
        """
        Get all stat boosts provided by this item.
        
        Returns:
            Dictionary mapping stat names to boost values
        """
        return self.stat_boosts.copy()
    
    def get_skill_boosts(self) -> Dict[str, float]:
        """
        Get all skill boosts provided by this item.
        
        Returns:
            Dictionary mapping skill names to boost values
        """
        return self.skill_boosts.copy()
    
    def get_stat_boost(self, stat_name: str) -> float:
        """
        Get boost for a specific stat.
        
        Args:
            stat_name: Name of the stat
            
        Returns:
            Boost value (0.0 if stat not boosted)
        """
        return self.stat_boosts.get(stat_name, 0.0)
    
    def get_skill_boost(self, skill_name: str) -> float:
        """
        Get boost for a specific skill.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Boost value (0.0 if skill not boosted)
        """
        return self.skill_boosts.get(skill_name, 0.0)

