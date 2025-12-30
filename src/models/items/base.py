"""Base Item class for all game items."""

from typing import Dict, Optional, Any, Tuple, List
from src.utils.constants import ITEM_TYPES, ELEMENTS, DEFAULT_ELEMENTAL_AFFINITY


class Item:
    """
    Base class for all items in the game.
    
    Attributes:
        name: Item name
        short_desc: Short description
        long_desc: Long description
        item_type: Type of item (weapon, wearable, consumable, etc.)
        weight_kg: Weight of the item in kilograms
        length_cm: Length of the item in centimeters
        width_cm: Width of the item in centimeters
        material: Material the item is made from
        restrictions: Dictionary of restrictions (e.g., stat requirements)
        affinities: Dictionary with 'elemental' and 'race' sub-dictionaries for affinity values.
                   Defaults to 1.0 for all elements and races.
        detriments: Dictionary with 'elemental' and 'race' sub-dictionaries for detriment values.
                   Defaults to 1.0 for all elements and races.
        auxiliary_slots: Number of auxiliary slots the item provides (default: 0)
        size_constraints: Tuple/list [min, max] for character size requirements (0-100 valid range).
                         If None, no size restrictions. Example: [20, 80] limits to characters
                         between size 20 and 80.
        thumbnail_path: Optional path to thumbnail/icon image (stored in GitHub, typically 200x200px)
    """
    
    def __init__(
        self,
        name: str,
        short_desc: str,
        long_desc: str,
        item_type: str,
        weight_kg: float,
        length_cm: float,
        width_cm: float,
        material: str,
        restrictions: Optional[Dict[str, Any]] = None,
        affinities: Optional[Dict[str, Dict[str, float]]] = None,
        detriments: Optional[Dict[str, Dict[str, float]]] = None,
        auxiliary_slots: int = 0,
        size_constraints: Optional[Tuple[float, float]] = None,
        thumbnail_path: Optional[str] = None,
    ):
        """
        Initialize an Item.
        
        Args:
            name: Item name
            short_desc: Short description
            long_desc: Long description
            item_type: Type of item (must be in ITEM_TYPES)
            weight_kg: Weight of the item in kilograms
            length_cm: Length of the item in centimeters
            width_cm: Width of the item in centimeters
            material: Material the item is made from
            restrictions: Optional dictionary of restrictions
            affinities: Optional dictionary with structure:
                       {
                         "elemental": {element_name: value, ...},
                         "race": {race_name: value, ...}
                       }
                       Defaults to 1.0 for all elements and races.
            detriments: Optional dictionary with structure:
                       {
                         "elemental": {element_name: value, ...},
                         "race": {race_name: value, ...}
                       }
                       Defaults to 1.0 for all elements and races.
            auxiliary_slots: Number of auxiliary slots the item provides (default: 0)
            size_constraints: Optional tuple/list [min, max] for character size requirements.
                            Valid range is 0-100. If None, no size restrictions.
                            Example: [20, 80] limits item to characters between size 20 and 80.
            thumbnail_path: Optional path to thumbnail/icon image (stored in GitHub, typically 200x200px)
        """
        self.name = name
        self.short_desc = short_desc
        self.long_desc = long_desc
        
        if item_type not in ITEM_TYPES:
            raise ValueError(f"Invalid item_type: {item_type}. Must be one of {ITEM_TYPES}")
        self.item_type = item_type
        
        self.weight_kg = weight_kg
        self.length_cm = length_cm
        self.width_cm = width_cm
        self.material = material
        self.restrictions = restrictions or {}
        
        # Initialize auxiliary_slots (default: 0)
        self.auxiliary_slots = auxiliary_slots
        
        # Initialize size_constraints with validation
        if size_constraints is not None:
            if isinstance(size_constraints, (list, tuple)) and len(size_constraints) == 2:
                min_size, max_size = size_constraints[0], size_constraints[1]
                if not (0 <= min_size <= 100 and 0 <= max_size <= 100):
                    raise ValueError("size_constraints values must be between 0 and 100")
                if min_size > max_size:
                    raise ValueError("size_constraints min must be <= max")
                self.size_constraints = (float(min_size), float(max_size))
            else:
                raise ValueError("size_constraints must be a tuple/list [min, max]")
        else:
            self.size_constraints = None
        
        # Initialize thumbnail_path
        self.thumbnail_path = thumbnail_path
        
        # Initialize affinities with default values
        self.affinities = {
            "elemental": {element: DEFAULT_ELEMENTAL_AFFINITY for element in ELEMENTS},
            "race": {},  # Will be populated when races are known
        }
        if affinities:
            if "elemental" in affinities:
                self.affinities["elemental"].update(affinities["elemental"])
            if "race" in affinities:
                self.affinities["race"].update(affinities["race"])
        
        # Initialize detriments with default values
        self.detriments = {
            "elemental": {element: DEFAULT_ELEMENTAL_AFFINITY for element in ELEMENTS},
            "race": {},  # Will be populated when races are known
        }
        if detriments:
            if "elemental" in detriments:
                self.detriments["elemental"].update(detriments["elemental"])
            if "race" in detriments:
                self.detriments["race"].update(detriments["race"])
    
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
            "weight_kg": self.weight_kg,
            "length_cm": self.length_cm,
            "width_cm": self.width_cm,
            "material": self.material,
            "restrictions": self.restrictions,
            "affinities": {
                "elemental": self.affinities["elemental"].copy(),
                "race": self.affinities["race"].copy(),
            },
            "detriments": {
                "elemental": self.detriments["elemental"].copy(),
                "race": self.detriments["race"].copy(),
            },
            "auxiliary_slots": self.auxiliary_slots,
            "size_constraints": list(self.size_constraints) if self.size_constraints else None,
            "thumbnail_path": self.thumbnail_path,
        }
    
    def get_elemental_affinity(self, element: str) -> float:
        """
        Get the elemental affinity value for a specific element.
        
        Args:
            element: Element name (must be in ELEMENTS)
            
        Returns:
            Affinity value (defaults to 1.0 if element not found)
        """
        return self.affinities["elemental"].get(element, DEFAULT_ELEMENTAL_AFFINITY)
    
    def set_elemental_affinity(self, element: str, value: float) -> None:
        """
        Set the elemental affinity value for a specific element.
        
        Args:
            element: Element name (must be in ELEMENTS)
            value: Affinity value
        """
        if element not in ELEMENTS:
            raise ValueError(f"Invalid element: {element}. Must be one of {ELEMENTS}")
        self.affinities["elemental"][element] = value
    
    def get_race_affinity(self, race: str) -> float:
        """
        Get the race affinity value for a specific race.
        
        Args:
            race: Race name
            
        Returns:
            Affinity value (defaults to 1.0 if race not found)
        """
        return self.affinities["race"].get(race, DEFAULT_ELEMENTAL_AFFINITY)
    
    def set_race_affinity(self, race: str, value: float) -> None:
        """
        Set the race affinity value for a specific race.
        
        Args:
            race: Race name
            value: Affinity value
        """
        self.affinities["race"][race] = value
    
    def get_elemental_detriment(self, element: str) -> float:
        """
        Get the elemental detriment value for a specific element.
        
        Args:
            element: Element name (must be in ELEMENTS)
            
        Returns:
            Detriment value (defaults to 1.0 if element not found)
        """
        return self.detriments["elemental"].get(element, DEFAULT_ELEMENTAL_AFFINITY)
    
    def set_elemental_detriment(self, element: str, value: float) -> None:
        """
        Set the elemental detriment value for a specific element.
        
        Args:
            element: Element name (must be in ELEMENTS)
            value: Detriment value
        """
        if element not in ELEMENTS:
            raise ValueError(f"Invalid element: {element}. Must be one of {ELEMENTS}")
        self.detriments["elemental"][element] = value
    
    def get_race_detriment(self, race: str) -> float:
        """
        Get the race detriment value for a specific race.
        
        Args:
            race: Race name
            
        Returns:
            Detriment value (defaults to 1.0 if race not found)
        """
        return self.detriments["race"].get(race, DEFAULT_ELEMENTAL_AFFINITY)
    
    def set_race_detriment(self, race: str, value: float) -> None:
        """
        Set the race detriment value for a specific race.
        
        Args:
            race: Race name
            value: Detriment value
        """
        self.detriments["race"][race] = value
    
    def can_use(self, character: Any) -> bool:
        """
        Check if a character can use this item based on restrictions and size constraints.
        
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
        
        # Check size constraints
        if self.size_constraints is not None:
            min_size, max_size = self.size_constraints
            character_size = None
            if hasattr(character, "get_stat"):
                character_size = character.get_stat("size")
            elif hasattr(character, "size"):
                character_size = getattr(character, "size")
            
            if character_size is not None:
                if not (min_size <= character_size <= max_size):
                    return False
        
        return True
    
    def set_size_constraints(self, min_size: float, max_size: float) -> None:
        """
        Set the size constraints for this item.
        
        Args:
            min_size: Minimum character size (0-100)
            max_size: Maximum character size (0-100)
            
        Raises:
            ValueError: If values are out of range or min > max
        """
        if not (0 <= min_size <= 100 and 0 <= max_size <= 100):
            raise ValueError("size_constraints values must be between 0 and 100")
        if min_size > max_size:
            raise ValueError("min_size must be <= max_size")
        self.size_constraints = (float(min_size), float(max_size))
    
    def clear_size_constraints(self) -> None:
        """Remove size constraints from this item (allow any size)."""
        self.size_constraints = None
    
    def get_size_constraints(self) -> Optional[Tuple[float, float]]:
        """
        Get the size constraints for this item.
        
        Returns:
            Tuple (min_size, max_size) if constraints exist, None otherwise
        """
        return self.size_constraints

