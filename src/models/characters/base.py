"""Base Character class for all characters."""

from typing import Dict, Any, Optional
import yaml
from pathlib import Path
from src.utils.constants import (
    CORE_STATS,
    AUXILIARY_STATS,
    ELEMENTS,
    CHARACTER_TYPES,
    CHARACTER_TYPE_PC,
    CHARACTER_TYPE_NPC,
    STAT_MIN,
    STAT_MAX,
    SKILL_LEVEL_MIN,
    SKILL_LEVEL_MAX,
    EQUIPMENT_SLOTS,
)
from src.utils.common.distributions import sample_gaussian


class Character:
    """
    Base class for all characters (PC and NPC).
    
    Characters have stats, skills, equipment, and various calculated attributes
    based on their stats. Stats are 0-100, and skills are level 0-100.
    
    Attributes:
        name: Character name
        race: Character race
        character_type: Type of character (PC or NPC)
        Core stats: str, constitution, dex, int, wis, luck (0-100)
        Auxiliary stats: physical_endurance, mental_endurance, charisma, eyesight, night_vision, stealth
        Elemental: affinities (dict), limitations (dict)
        Skills: skill_levels (dict mapping skill_name:level 0-100)
        Equipment: equipped_items (dict mapping slot:item)
    """
    
    def __init__(
        self,
        name: str,
        race: str,
        character_type: str,
        stat_points_to_distribute: int = 20,
    ):
        """
        Initialize a character with race-based stat initialization.
        
        Args:
            name: Character name
            race: Character race (must exist in race data)
            character_type: Type of character (PC or NPC)
            stat_points_to_distribute: Additional stat points to distribute (default 20)
        """
        self.name = name
        self.race = race
        self.character_type = character_type
        
        if character_type not in CHARACTER_TYPES:
            raise ValueError(f"Invalid character_type: {character_type}")
        
        # Load race data
        race_data = self._load_race_data(race)
        
        # Initialize core stats
        self._initialize_core_stats(race_data, stat_points_to_distribute)
        
        # Initialize auxiliary stats
        self._initialize_auxiliary_stats(race_data)
        
        # Initialize elemental attributes
        self._initialize_elemental_attributes(race_data)
        
        # Initialize skills and equipment
        self.skill_levels: Dict[str, int] = {}
        self.equipped_items: Dict[str, Any] = {}
    
    def _load_race_data(self, race: str) -> Dict[str, Any]:
        """
        Load race data from YAML file.
        
        Args:
            race: Race name
            
        Returns:
            Dictionary containing race data
            
        Raises:
            FileNotFoundError: If race data file not found
            KeyError: If race not found in data
        """
        # Get path to race data file
        data_file = Path(__file__).parent.parent.parent / "data" / "races.yaml"
        
        if not data_file.exists():
            raise FileNotFoundError(f"Race data file not found: {data_file}")
        
        with open(data_file, "r") as f:
            data = yaml.safe_load(f)
        
        if "races" not in data or race not in data["races"]:
            raise KeyError(f"Race '{race}' not found in race data")
        
        return data["races"][race]
    
    def _initialize_core_stats(
        self, race_data: Dict[str, Any], stat_points: int
    ) -> None:
        """
        Initialize core stats based on race data.
        
        Args:
            race_data: Race data dictionary
            stat_points: Additional stat points to distribute
        """
        stat_min = race_data.get("stat_min", {})
        stat_max = race_data.get("stat_max", {})
        initial_mean = race_data.get("initial_mean", {})
        initial_std = race_data.get("initial_std", {})
        
        # Initialize each core stat
        for stat in CORE_STATS:
            # Get race-specific values or defaults
            min_val = stat_min.get(stat, STAT_MIN)
            max_val = stat_max.get(stat, STAT_MAX)
            mean = initial_mean.get(stat, 50)
            std = initial_std.get(stat, 5)
            
            # Sample from distribution
            value = sample_gaussian(mean, std)
            
            # Clamp to min/max
            value = max(min_val, min(max_val, value))
            
            # Round to integer
            setattr(self, stat, int(value))
        
        # Distribute additional stat points (placeholder - would be done by PC class)
        # For base class, we just set the stats as rolled
        pass
    
    def _initialize_auxiliary_stats(self, race_data: Dict[str, Any]) -> None:
        """
        Initialize auxiliary stats based on race data.
        
        Args:
            race_data: Race data dictionary
        """
        defaults = race_data.get("auxiliary_defaults", {})
        
        for stat in AUXILIARY_STATS:
            value = defaults.get(stat, 50)
            setattr(self, stat, value)
    
    def _initialize_elemental_attributes(self, race_data: Dict[str, Any]) -> None:
        """
        Initialize elemental affinities and limitations.
        
        Args:
            race_data: Race data dictionary
        """
        self.affinities = race_data.get("elemental_affinities", {}).copy()
        self.limitations = race_data.get("elemental_limitations", {}).copy()
        
        # Ensure all elements are present
        for element in ELEMENTS:
            if element not in self.affinities:
                self.affinities[element] = 0
            if element not in self.limitations:
                self.limitations[element] = 0
    
    def get_stat(self, stat_name: str) -> int:
        """
        Get a stat value by name.
        
        Args:
            stat_name: Name of the stat
            
        Returns:
            Stat value
        """
        if hasattr(self, stat_name):
            return getattr(self, stat_name)
        raise AttributeError(f"Stat '{stat_name}' not found")
    
    def set_stat(self, stat_name: str, value: int) -> None:
        """
        Set a stat value, clamping to valid range.
        
        Args:
            stat_name: Name of the stat
            value: Value to set
        """
        # Clamp to valid range
        value = max(STAT_MIN, min(STAT_MAX, int(value)))
        setattr(self, stat_name, value)
    
    def calculate_damage_modifier(self) -> float:
        """
        Calculate damage modifier based on strength.
        
        Returns:
            Damage modifier multiplier
        """
        # Placeholder formula: modifier = 1 + (str / 100)
        str_stat = self.get_stat("str")
        return 1.0 + (str_stat / 100.0)
    
    def calculate_speed(self) -> float:
        """
        Calculate speed based on dexterity.
        
        Returns:
            Speed value
        """
        # Placeholder formula: speed = base_speed * (1 + dex / 100)
        dex_stat = self.get_stat("dex")
        base_speed = 1.0
        return base_speed * (1.0 + (dex_stat / 100.0))
    
    def calculate_hit_probability(self, weapon_skill_level: int = 0) -> float:
        """
        Calculate hit probability based on dexterity and weapon skill.
        
        Args:
            weapon_skill_level: Level of weapon skill (0-100)
            
        Returns:
            Hit probability (0.0 to 1.0)
        """
        # Placeholder formula: p_hit = base + (dex / 100) + (skill_level / 200)
        dex_stat = self.get_stat("dex")
        base_prob = 0.5
        dex_bonus = dex_stat / 100.0
        skill_bonus = weapon_skill_level / 200.0
        
        probability = base_prob + dex_bonus + skill_bonus
        return max(0.0, min(1.0, probability))
    
    def calculate_dodge(self) -> float:
        """
        Calculate dodge probability based on dexterity.
        
        Returns:
            Dodge probability (0.0 to 1.0)
        """
        # Placeholder formula: dodge = base + (dex / 150)
        dex_stat = self.get_stat("dex")
        base_dodge = 0.1
        dex_bonus = dex_stat / 150.0
        
        probability = base_dodge + dex_bonus
        return max(0.0, min(1.0, probability))
    
    def calculate_spell_speed(self) -> float:
        """
        Calculate spell casting speed based on intelligence.
        
        Returns:
            Spell speed value
        """
        # Placeholder formula: speed = base_speed * (1 + int / 100)
        int_stat = self.get_stat("int")
        base_speed = 1.0
        return base_speed * (1.0 + (int_stat / 100.0))
    
    def calculate_spell_success(self) -> float:
        """
        Calculate spell success probability based on intelligence and wisdom.
        
        Returns:
            Spell success probability (0.0 to 1.0)
        """
        # Placeholder formula: p_success = base + ((int + wis) / 200)
        int_stat = self.get_stat("int")
        wis_stat = self.get_stat("wis")
        base_prob = 0.5
        stat_bonus = (int_stat + wis_stat) / 200.0
        
        probability = base_prob + stat_bonus
        return max(0.0, min(1.0, probability))
    
    def calculate_hp_regen(self) -> float:
        """
        Calculate HP regeneration rate based on constitution.
        
        Returns:
            HP regeneration per turn
        """
        # Placeholder formula: regen = base_regen * (1 + constitution / 100)
        con_stat = self.get_stat("constitution")
        base_regen = 1.0
        return base_regen * (1.0 + (con_stat / 100.0))
    
    def calculate_mana_regen(self) -> float:
        """
        Calculate mana regeneration rate based on wisdom.
        
        Returns:
            Mana regeneration per turn
        """
        # Placeholder formula: regen = base_regen * (1 + wis / 100)
        wis_stat = self.get_stat("wis")
        base_regen = 1.0
        return base_regen * (1.0 + (wis_stat / 100.0))
    
    def get_weight_capacity(self) -> float:
        """
        Calculate weight carrying capacity based on strength.
        
        Returns:
            Maximum weight that can be carried
        """
        # Placeholder formula: capacity = base_capacity * (1 + str / 50)
        str_stat = self.get_stat("str")
        base_capacity = 50.0
        return base_capacity * (1.0 + (str_stat / 50.0))
    
    def get_skill_level(self, skill_name: str) -> int:
        """
        Get the level of a skill.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Skill level (0-100), or 0 if skill not known
        """
        return self.skill_levels.get(skill_name, SKILL_LEVEL_MIN)
    
    def learn_skill(self, skill: Any, level: int = 0) -> bool:
        """
        Learn a skill or set its level.
        
        Args:
            skill: Skill object to learn
            level: Initial level (default 0)
            
        Returns:
            True if skill was learned, False otherwise
        """
        if not hasattr(skill, "name"):
            return False
        
        # Check if character can learn the skill
        if hasattr(skill, "can_learn"):
            if not skill.can_learn(self):
                return False
        
        # Clamp level to valid range
        level = max(SKILL_LEVEL_MIN, min(SKILL_LEVEL_MAX, level))
        
        self.skill_levels[skill.name] = level
        return True
    
    def can_equip(self, item: Any) -> bool:
        """
        Check if character can equip an item.
        
        Args:
            item: Item to check
            
        Returns:
            True if item can be equipped, False otherwise
        """
        # Check if item has can_use method
        if hasattr(item, "can_use"):
            if not item.can_use(self):
                return False
        
        # Check weight capacity
        if hasattr(item, "weight"):
            total_weight = sum(
                i.weight for i in self.equipped_items.values() if hasattr(i, "weight")
            )
            if total_weight + item.weight > self.get_weight_capacity():
                return False
        
        return True
    
    def equip_item(self, item: Any, slot: Optional[str] = None) -> bool:
        """
        Equip an item to a slot.
        
        Args:
            item: Item to equip
            slot: Slot to equip to (if None, uses item's slot attribute)
            
        Returns:
            True if item was equipped, False otherwise
        """
        if not self.can_equip(item):
            return False
        
        # Determine slot
        if slot is None:
            if hasattr(item, "slot"):
                slot = item.slot
            else:
                return False
        
        if slot not in EQUIPMENT_SLOTS:
            return False
        
        # Unequip existing item in slot if any
        if slot in self.equipped_items:
            self.unequip_item(slot)
        
        self.equipped_items[slot] = item
        return True
    
    def unequip_item(self, slot: str) -> bool:
        """
        Unequip an item from a slot.
        
        Args:
            slot: Slot to unequip from
            
        Returns:
            True if item was unequipped, False otherwise
        """
        if slot in self.equipped_items:
            del self.equipped_items[slot]
            return True
        return False

