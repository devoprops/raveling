"""Attack skill subclasses."""

from typing import Dict, Any, Optional
from src.models.skills.base import Skill
from src.utils.constants import SKILL_TYPE_ATTACK, ATTACK_PHYSICAL, ATTACK_ELEMENTAL, ELEMENTS


class PhysicalAttack(Skill):
    """
    Physical attack skill.
    
    Attributes:
        base_damage: Base damage value
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        base_damage: float,
        min_requirements: Optional[Dict[str, int]] = None,
    ):
        """
        Initialize a physical attack skill.
        
        Args:
            name: Skill name
            description: Skill description
            base_damage: Base damage value
            min_requirements: Optional minimum stat requirements
        """
        super().__init__(
            name=name,
            skill_type=SKILL_TYPE_ATTACK,
            subtype=ATTACK_PHYSICAL,
            description=description,
            min_requirements=min_requirements,
        )
        self.base_damage = base_damage
    
    def calculate_damage(self, character: Any, target: Any) -> float:
        """
        Calculate damage dealt by this physical attack.
        
        Args:
            character: Character using the skill
            target: Target character
            
        Returns:
            Damage amount
        """
        # Placeholder formula:
        # damage = base_damage * (1 + str / 100) * (1 + dex / 200) * skill_level_multiplier
        
        # Get skill level
        skill_level = 0
        if hasattr(character, "get_skill_level"):
            skill_level = character.get_skill_level(self.name)
        
        # Skill level multiplier
        skill_multiplier = 1.0 + (skill_level / 100.0)
        
        # Get stats
        str_stat = 0
        dex_stat = 0
        if hasattr(character, "get_stat"):
            str_stat = character.get_stat("str")
            dex_stat = character.get_stat("dex")
        elif hasattr(character, "str"):
            str_stat = character.str
            dex_stat = character.dex
        
        # Calculate damage
        str_multiplier = 1.0 + (str_stat / 100.0)
        dex_multiplier = 1.0 + (dex_stat / 200.0)
        
        damage = self.base_damage * str_multiplier * dex_multiplier * skill_multiplier
        
        return max(0.0, damage)
    
    def calculate_hit_probability(self, character: Any, target: Any) -> float:
        """
        Calculate probability of hitting the target.
        
        Args:
            character: Character using the skill
            target: Target character
            
        Returns:
            Hit probability (0.0 to 1.0)
        """
        # Placeholder formula:
        # p_hit = base + (dex / 100) + (skill_level / 200) - (target_dodge / 100)
        
        # Get skill level
        skill_level = 0
        if hasattr(character, "get_skill_level"):
            skill_level = character.get_skill_level(self.name)
        
        # Get character dex
        dex_stat = 0
        if hasattr(character, "get_stat"):
            dex_stat = character.get_stat("dex")
        elif hasattr(character, "dex"):
            dex_stat = character.dex
        
        # Get target dodge
        target_dodge = 0
        if hasattr(target, "calculate_dodge"):
            target_dodge = target.calculate_dodge()
        elif hasattr(target, "get_stat"):
            target_dodge = target.get_stat("dex") / 100.0
        
        # Base hit probability
        base_prob = 0.5
        
        # Calculate final probability
        probability = base_prob + (dex_stat / 100.0) + (skill_level / 200.0) - (target_dodge / 100.0)
        
        # Clamp to valid range
        return max(0.0, min(1.0, probability))
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the physical attack.
        
        Args:
            character: Character using the skill
            target: Target character
            
        Returns:
            Dictionary with attack results
        """
        import random
        
        # Check if attack hits
        hit_prob = self.calculate_hit_probability(character, target)
        hit = random.random() < hit_prob
        
        if hit:
            damage = self.calculate_damage(character, target)
            return {
                "success": True,
                "hit": True,
                "damage": damage,
                "damage_type": "physical",
            }
        else:
            return {
                "success": True,
                "hit": False,
                "damage": 0.0,
            }


class ElementalAttack(Skill):
    """
    Elemental attack skill (spell).
    
    Attributes:
        base_damage: Base damage value
        element_type: Type of element (fire, water, etc.)
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        base_damage: float,
        element_type: str,
        min_requirements: Optional[Dict[str, int]] = None,
    ):
        """
        Initialize an elemental attack skill.
        
        Args:
            name: Skill name
            description: Skill description
            base_damage: Base damage value
            element_type: Type of element (must be in ELEMENTS)
            min_requirements: Optional minimum stat requirements
        """
        super().__init__(
            name=name,
            skill_type=SKILL_TYPE_ATTACK,
            subtype=ATTACK_ELEMENTAL,
            description=description,
            min_requirements=min_requirements,
        )
        
        if element_type not in ELEMENTS:
            raise ValueError(f"Invalid element_type: {element_type}")
        self.element_type = element_type
        self.base_damage = base_damage
    
    def calculate_damage(self, character: Any, target: Any) -> float:
        """
        Calculate damage dealt by this elemental attack.
        
        Args:
            character: Character using the skill
            target: Target character
            
        Returns:
            Damage amount
        """
        # Placeholder formula:
        # damage = base_damage * (1 + (int + wis) / 200) * elemental_affinity_multiplier * skill_level_multiplier
        
        # Get skill level
        skill_level = 0
        if hasattr(character, "get_skill_level"):
            skill_level = character.get_skill_level(self.name)
        
        # Skill level multiplier
        skill_multiplier = 1.0 + (skill_level / 100.0)
        
        # Get stats
        int_stat = 0
        wis_stat = 0
        if hasattr(character, "get_stat"):
            int_stat = character.get_stat("int")
            wis_stat = character.get_stat("wis")
        elif hasattr(character, "int"):
            int_stat = character.int
            wis_stat = character.wis
        
        # Calculate stat multiplier
        stat_multiplier = 1.0 + ((int_stat + wis_stat) / 200.0)
        
        # Get elemental affinity
        elemental_multiplier = 1.0
        if hasattr(character, "affinities") and self.element_type in character.affinities:
            affinity = character.affinities[self.element_type]
            elemental_multiplier = 1.0 + (affinity / 100.0)
        
        # Calculate damage
        damage = self.base_damage * stat_multiplier * elemental_multiplier * skill_multiplier
        
        return max(0.0, damage)
    
    def calculate_hit_probability(self, character: Any, target: Any) -> float:
        """
        Calculate probability of spell hitting the target.
        
        Args:
            character: Character using the skill
            target: Target character
            
        Returns:
            Hit probability (0.0 to 1.0)
        """
        # Placeholder formula:
        # p_hit = base + (int / 100) + (skill_level / 200) - (target_resistance / 100)
        
        # Get skill level
        skill_level = 0
        if hasattr(character, "get_skill_level"):
            skill_level = character.get_skill_level(self.name)
        
        # Get character int
        int_stat = 0
        if hasattr(character, "get_stat"):
            int_stat = character.get_stat("int")
        elif hasattr(character, "int"):
            int_stat = character.int
        
        # Get target resistance (placeholder - would check elemental resistance)
        target_resistance = 0
        if hasattr(target, "limitations") and self.element_type in target.limitations:
            target_resistance = abs(target.limitations[self.element_type])
        
        # Base hit probability
        base_prob = 0.5
        
        # Calculate final probability
        probability = base_prob + (int_stat / 100.0) + (skill_level / 200.0) - (target_resistance / 100.0)
        
        # Clamp to valid range
        return max(0.0, min(1.0, probability))
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the elemental attack.
        
        Args:
            character: Character using the skill
            target: Target character
            
        Returns:
            Dictionary with attack results
        """
        import random
        
        # Check success probability (for spells, this is separate from hit)
        success_prob = self.calculate_success_probability(character)
        success = random.random() < success_prob
        
        if not success:
            return {
                "success": False,
                "hit": False,
                "damage": 0.0,
            }
        
        # Check if spell hits
        hit_prob = self.calculate_hit_probability(character, target)
        hit = random.random() < hit_prob
        
        if hit:
            damage = self.calculate_damage(character, target)
            return {
                "success": True,
                "hit": True,
                "damage": damage,
                "damage_type": "elemental",
                "element": self.element_type,
            }
        else:
            return {
                "success": True,
                "hit": False,
                "damage": 0.0,
            }

