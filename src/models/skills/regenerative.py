"""Regenerative skill class."""

from typing import Dict, Any, Optional
from src.models.skills.base import Skill
from src.utils.constants import SKILL_TYPE_REGENERATIVE, REGEN_TYPES


class Regenerative(Skill):
    """
    Regenerative skill that replenishes HP, mana, stamina, etc.
    
    Attributes:
        regen_type: Type of regeneration (hp, mana, stamina)
        base_amount: Base amount to regenerate
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        regen_type: str,
        base_amount: float,
        min_requirements: Optional[Dict[str, int]] = None,
    ):
        """
        Initialize a regenerative skill.
        
        Args:
            name: Skill name
            description: Skill description
            regen_type: Type of regeneration (must be in REGEN_TYPES)
            base_amount: Base amount to regenerate
            min_requirements: Optional minimum stat requirements
        """
        super().__init__(
            name=name,
            skill_type=SKILL_TYPE_REGENERATIVE,
            subtype=regen_type,
            description=description,
            min_requirements=min_requirements,
        )
        
        if regen_type not in REGEN_TYPES:
            raise ValueError(f"Invalid regen_type: {regen_type}")
        self.regen_type = regen_type
        self.base_amount = base_amount
    
    def calculate_regen_amount(self, character: Any) -> float:
        """
        Calculate the amount to regenerate based on character stats.
        
        Args:
            character: Character using the skill
            
        Returns:
            Amount to regenerate
        """
        # Placeholder formulas:
        # For HP: amount = base_amount * (1 + constitution / 100) * skill_level_multiplier
        # For mana: amount = base_amount * (1 + wis / 100) * skill_level_multiplier
        # For stamina: amount = base_amount * (1 + physical_endurance / 100) * skill_level_multiplier
        
        # Get skill level
        skill_level = 0
        if hasattr(character, "get_skill_level"):
            skill_level = character.get_skill_level(self.name)
        
        # Skill level multiplier
        skill_multiplier = 1.0 + (skill_level / 100.0)
        
        # Get relevant stat based on regen type
        stat_value = 0
        if self.regen_type == REGEN_TYPE_HP:
            if hasattr(character, "get_stat"):
                stat_value = character.get_stat("constitution")
            elif hasattr(character, "constitution"):
                stat_value = character.constitution
        elif self.regen_type == REGEN_TYPE_MANA:
            if hasattr(character, "get_stat"):
                stat_value = character.get_stat("wis")
            elif hasattr(character, "wis"):
                stat_value = character.wis
        elif self.regen_type == REGEN_TYPE_STAMINA:
            if hasattr(character, "get_stat"):
                stat_value = character.get_stat("physical_endurance")
            elif hasattr(character, "physical_endurance"):
                stat_value = character.physical_endurance
        
        # Calculate stat multiplier
        stat_multiplier = 1.0 + (stat_value / 100.0)
        
        # Calculate regen amount
        amount = self.base_amount * stat_multiplier * skill_multiplier
        
        return max(0.0, amount)
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the regenerative skill.
        
        Args:
            character: Character using the skill
            target: Target character (usually same as character for self-heal)
            
        Returns:
            Dictionary with regeneration results
        """
        # Check success probability
        success_prob = self.calculate_success_probability(character)
        import random
        success = random.random() < success_prob
        
        if not success:
            return {
                "success": False,
                "regen_amount": 0.0,
            }
        
        # Calculate regen amount
        regen_amount = self.calculate_regen_amount(character)
        
        return {
            "success": True,
            "regen_type": self.regen_type,
            "regen_amount": regen_amount,
        }

