"""Base Skill class for all skills and spells."""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from src.utils.constants import SKILL_TYPES


class Skill(ABC):
    """
    Base class for all skills and spells.
    
    Skills and spells are heavily tied to stats and skill level rather than
    player level. They may have minimum stat requirements to learn.
    
    Attributes:
        name: Skill name
        skill_type: Type of skill (attack, buff, debuff, regenerative, process)
        subtype: Subtype of skill (e.g., physical, elemental for attacks)
        description: Description of the skill
        min_requirements: Dictionary mapping stat names to minimum values required
    """
    
    def __init__(
        self,
        name: str,
        skill_type: str,
        subtype: str,
        description: str,
        min_requirements: Optional[Dict[str, int]] = None,
    ):
        """
        Initialize a skill.
        
        Args:
            name: Skill name
            skill_type: Type of skill (must be in SKILL_TYPES)
            subtype: Subtype of skill
            description: Description of the skill
            min_requirements: Dictionary of stat name -> minimum value required
        """
        if skill_type not in SKILL_TYPES:
            raise ValueError(f"Invalid skill_type: {skill_type}")
        
        self.name = name
        self.skill_type = skill_type
        self.subtype = subtype
        self.description = description
        self.min_requirements = min_requirements or {}
    
    def can_learn(self, character: Any) -> bool:
        """
        Check if a character can learn this skill based on minimum requirements.
        
        Args:
            character: Character to check
            
        Returns:
            True if character meets requirements, False otherwise
        """
        for stat_name, min_value in self.min_requirements.items():
            if hasattr(character, "get_stat"):
                if character.get_stat(stat_name) < min_value:
                    return False
            elif hasattr(character, stat_name):
                if getattr(character, stat_name) < min_value:
                    return False
        return True
    
    def calculate_success_probability(self, character: Any) -> float:
        """
        Calculate the probability of skill success based on character stats.
        
        For magical effects, heavily based on INT/WIS. For physical, based on
        relevant physical stats.
        
        Args:
            character: Character using the skill
            
        Returns:
            Probability of success (0.0 to 1.0)
        """
        # Placeholder formula:
        # For magical skills: p_success = base + (int + wis) / 200 * skill_level_multiplier
        # For physical skills: p_success = base + (dex + str) / 200 * skill_level_multiplier
        
        # Get skill level
        skill_level = 0
        if hasattr(character, "get_skill_level"):
            skill_level = character.get_skill_level(self.name)
        
        # Base success probability
        base_prob = 0.5
        
        # Apply stat modifiers based on skill type
        if self.skill_type == "attack" and self.subtype == "elemental":
            # Magical attack
            if hasattr(character, "get_stat"):
                int_stat = character.get_stat("int")
                wis_stat = character.get_stat("wis")
                stat_bonus = (int_stat + wis_stat) / 200.0
            else:
                stat_bonus = 0.0
        else:
            # Physical or other
            if hasattr(character, "get_stat"):
                dex_stat = character.get_stat("dex")
                str_stat = character.get_stat("str")
                stat_bonus = (dex_stat + str_stat) / 200.0
            else:
                stat_bonus = 0.0
        
        # Skill level multiplier (0-100 -> 0.0-1.0 multiplier)
        skill_multiplier = skill_level / 100.0
        
        # Calculate final probability
        probability = base_prob + (stat_bonus * skill_multiplier)
        
        # Clamp to valid range
        return max(0.0, min(1.0, probability))
    
    def calculate_effect_magnitude(self, character: Any) -> float:
        """
        Calculate the magnitude/strength of the skill effect.
        
        For magical effects, heavily based on WIS. For physical, based on STR/DEX.
        
        Args:
            character: Character using the skill
            
        Returns:
            Effect magnitude value
        """
        # Placeholder formula:
        # For magical: magnitude = base * (1 + wis / 100) * skill_level_multiplier
        # For physical: magnitude = base * (1 + str / 100) * skill_level_multiplier
        
        # Get skill level
        skill_level = 0
        if hasattr(character, "get_skill_level"):
            skill_level = character.get_skill_level(self.name)
        
        # Skill level multiplier (0-100 -> 0.0-1.0 multiplier, then add 1.0)
        skill_multiplier = 1.0 + (skill_level / 100.0)
        
        # Apply stat modifiers based on skill type
        if self.skill_type == "attack" and self.subtype == "elemental":
            # Magical effect
            if hasattr(character, "get_stat"):
                wis_stat = character.get_stat("wis")
                stat_multiplier = 1.0 + (wis_stat / 100.0)
            else:
                stat_multiplier = 1.0
        else:
            # Physical or other
            if hasattr(character, "get_stat"):
                str_stat = character.get_stat("str")
                stat_multiplier = 1.0 + (str_stat / 100.0)
            else:
                stat_multiplier = 1.0
        
        # Base magnitude (to be overridden by subclasses)
        base_magnitude = 1.0
        
        return base_magnitude * stat_multiplier * skill_multiplier
    
    @abstractmethod
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the skill and return results.
        
        Args:
            character: Character using the skill
            target: Target character or object
            
        Returns:
            Dictionary containing skill execution results
        """
        pass

