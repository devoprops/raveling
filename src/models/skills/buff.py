"""Buff skill class."""

from typing import Dict, Any, Optional
from src.models.skills.base import Skill
from src.utils.constants import SKILL_TYPE_BUFF


class Buff(Skill):
    """
    Buff skill that increases stats, resistance, or other attributes.
    
    Attributes:
        stat_modifiers: Dictionary mapping stat names to modifier values
        base_duration: Base duration of the buff in turns
        magnitude: Magnitude of the effect
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        stat_modifiers: Dict[str, float],
        base_duration: int,
        magnitude: float = 1.0,
        min_requirements: Optional[Dict[str, int]] = None,
    ):
        """
        Initialize a buff skill.
        
        Args:
            name: Skill name
            description: Skill description
            stat_modifiers: Dictionary of stat name -> modifier value
            base_duration: Base duration in turns
            magnitude: Magnitude of the effect
            min_requirements: Optional minimum stat requirements
        """
        super().__init__(
            name=name,
            skill_type=SKILL_TYPE_BUFF,
            subtype="stat_boost",
            description=description,
            min_requirements=min_requirements,
        )
        self.stat_modifiers = stat_modifiers
        self.base_duration = base_duration
        self.magnitude = magnitude
    
    def calculate_duration(self, character: Any) -> int:
        """
        Calculate the duration of the buff based on character stats.
        
        Args:
            character: Character using the skill
            
        Returns:
            Duration in turns
        """
        # Placeholder formula:
        # duration = base_duration * (1 + wis / 200) * skill_level_multiplier
        
        # Get skill level
        skill_level = 0
        if hasattr(character, "get_skill_level"):
            skill_level = character.get_skill_level(self.name)
        
        # Skill level multiplier
        skill_multiplier = 1.0 + (skill_level / 200.0)
        
        # Get wis stat
        wis_stat = 0
        if hasattr(character, "get_stat"):
            wis_stat = character.get_stat("wis")
        elif hasattr(character, "wis"):
            wis_stat = character.wis
        
        # Calculate duration
        wis_multiplier = 1.0 + (wis_stat / 200.0)
        duration = int(self.base_duration * wis_multiplier * skill_multiplier)
        
        return max(1, duration)
    
    def apply_effect(self, character: Any) -> Dict[str, Any]:
        """
        Apply the buff effect to a character.
        
        Args:
            character: Character to apply buff to
            
        Returns:
            Dictionary with applied effects
        """
        # Calculate actual modifiers with magnitude
        applied_modifiers = {}
        for stat_name, modifier in self.stat_modifiers.items():
            applied_modifiers[stat_name] = modifier * self.magnitude
        
        # Calculate duration
        duration = self.calculate_duration(character)
        
        return {
            "stat_modifiers": applied_modifiers,
            "duration": duration,
            "magnitude": self.magnitude,
        }
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the buff skill.
        
        Args:
            character: Character using the skill
            target: Target character (usually same as character for self-buff)
            
        Returns:
            Dictionary with buff application results
        """
        # Check success probability
        success_prob = self.calculate_success_probability(character)
        import random
        success = random.random() < success_prob
        
        if not success:
            return {
                "success": False,
                "applied": False,
            }
        
        # Apply effect
        effect = self.apply_effect(target)
        
        return {
            "success": True,
            "applied": True,
            "effect": effect,
        }

