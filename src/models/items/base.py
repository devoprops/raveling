"""Base Item class for all game items."""

from typing import Dict, Optional, Any
from src.utils.constants import ITEM_TYPES


class Item:
    """
    Base class for all items in the game.
    
    Attributes:
        name: Item name
        short_desc: Short description
        long_desc: Long description
        item_type: Type of item (weapon, wearable, consumable, etc.)
        weight: Weight of the item
        size: Size of the item
        material: Material the item is made from
        restrictions: Dictionary of restrictions (e.g., stat requirements)
    """
    
    def __init__(
        self,
        name: str,
        short_desc: str,
        long_desc: str,
        item_type: str,
        weight: float,
        size: float,
        material: str,
        restrictions: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize an Item.
        
        Args:
            name: Item name
            short_desc: Short description
            long_desc: Long description
            item_type: Type of item (must be in ITEM_TYPES)
            weight: Weight of the item
            size: Size of the item
            material: Material the item is made from
            restrictions: Optional dictionary of restrictions
        """
        self.name = name
        self.short_desc = short_desc
        self.long_desc = long_desc
        
        if item_type not in ITEM_TYPES:
            raise ValueError(f"Invalid item_type: {item_type}. Must be one of {ITEM_TYPES}")
        self.item_type = item_type
        
        self.weight = weight
        self.size = size
        self.material = material
        self.restrictions = restrictions or {}
    
    def __repr__(self) -> str:
        """Return string representation of the item."""
        return f"Item(name='{self.name}', type='{self.item_type}')"
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get complete information about the item.
        
        Returns:
            Dictionary containing all item information
        """
        return {
            "name": self.name,
            "short_desc": self.short_desc,
            "long_desc": self.long_desc,
            "item_type": self.item_type,
            "weight": self.weight,
            "size": self.size,
            "material": self.material,
            "restrictions": self.restrictions,
        }
    
    def can_use(self, character: Any) -> bool:
        """
        Check if a character can use this item based on restrictions.
        
        Args:
            character: Character object to check
            
        Returns:
            True if character can use the item, False otherwise
        """
        # Check stat requirements
        if "stats" in self.restrictions:
            for stat_name, min_value in self.restrictions["stats"].items():
                if hasattr(character, "get_stat"):
                    if character.get_stat(stat_name) < min_value:
                        return False
                elif hasattr(character, stat_name):
                    if getattr(character, stat_name) < min_value:
                        return False
        
        # Check other restrictions (race, level, etc.)
        if "race" in self.restrictions:
            if hasattr(character, "race"):
                if character.race not in self.restrictions["race"]:
                    return False
        
        return True

