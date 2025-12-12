"""Damage node classes for weapon damage calculations."""

from typing import Dict, Any, Optional, Callable, Union
from abc import ABC, abstractmethod
from src.utils.constants import (
    DAMAGE_NODE_TYPES,
    DAMAGE_NODE_PRIMARY,
    DAMAGE_NODE_SECONDARY,
    DAMAGE_NODE_SKILL,
    DAMAGE_NODE_SPELL,
    DAMAGE_NODE_PROCESS,
    ELEMENTS,
)
from src.utils.common.distributions import DistributionFunction


class DamageNode(ABC):
    """
    Base class for damage nodes in weapon damage calculations.
    
    Each damage node represents a potential source of damage or effect that can
    be triggered when a weapon is used. Nodes are evaluated independently based
    on their execution probability.
    
    Attributes:
        node_type: Type of node (primary, secondary, skill, spell, process)
        execution_probability: Probability of this node executing (0.0 to 1.0)
    """
    
    def __init__(
        self,
        node_type: str,
        execution_probability: float,
    ):
        """
        Initialize a damage node.
        
        Args:
            node_type: Type of node (must be in DAMAGE_NODE_TYPES)
            execution_probability: Probability of execution (0.0 to 1.0)
        """
        if node_type not in DAMAGE_NODE_TYPES:
            raise ValueError(f"Invalid node_type: {node_type}")
        self.node_type = node_type
        
        if not 0.0 <= execution_probability <= 1.0:
            raise ValueError("execution_probability must be between 0.0 and 1.0")
        self.execution_probability = execution_probability
    
    @abstractmethod
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the damage node and return results.
        
        Args:
            character: Character using the weapon
            target: Target character or object
            
        Returns:
            Dictionary containing damage/effect results
        """
        pass


class PhysicalDamageNode(DamageNode):
    """
    Physical damage node that applies physical damage using a distribution model.
    
    Attributes:
        damage_model: Distribution function to sample damage from
        base_damage: Base damage value (used with distribution)
    """
    
    def __init__(
        self,
        node_type: str,
        execution_probability: float,
        damage_model: DistributionFunction,
        base_damage: float = 0.0,
    ):
        """
        Initialize a physical damage node.
        
        Args:
            node_type: Type of node (primary, secondary, etc.)
            execution_probability: Probability of execution
            damage_model: Function that returns damage value when called
            base_damage: Base damage value (if needed by damage_model)
        """
        super().__init__(node_type, execution_probability)
        self.damage_model = damage_model
        self.base_damage = base_damage
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute physical damage calculation.
        
        Args:
            character: Character using the weapon
            target: Target character
            
        Returns:
            Dictionary with damage type, amount, and other effects
        """
        # Sample damage from distribution model
        damage = self.damage_model()
        
        # Apply character stat modifiers (placeholder for future implementation)
        # damage = damage * (1 + character.get_stat("str") / 100) * skill_multiplier
        
        return {
            "damage_type": "physical",
            "amount": max(0.0, damage),
            "node_type": self.node_type,
        }


class ElementalDamageNode(DamageNode):
    """
    Elemental damage node that applies elemental damage.
    
    Attributes:
        element_type: Type of element (fire, water, etc.)
        damage_model: Distribution function to sample damage from
        base_damage: Base damage value
    """
    
    def __init__(
        self,
        node_type: str,
        execution_probability: float,
        element_type: str,
        damage_model: DistributionFunction,
        base_damage: float = 0.0,
    ):
        """
        Initialize an elemental damage node.
        
        Args:
            node_type: Type of node (primary, secondary, etc.)
            execution_probability: Probability of execution
            element_type: Type of element (must be in ELEMENTS)
            damage_model: Function that returns damage value when called
            base_damage: Base damage value
        """
        super().__init__(node_type, execution_probability)
        
        if element_type not in ELEMENTS:
            raise ValueError(f"Invalid element_type: {element_type}")
        self.element_type = element_type
        
        self.damage_model = damage_model
        self.base_damage = base_damage
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute elemental damage calculation.
        
        Args:
            character: Character using the weapon
            target: Target character
            
        Returns:
            Dictionary with damage type, element, amount, and other effects
        """
        # Sample damage from distribution model
        damage = self.damage_model()
        
        # Apply character stat modifiers (placeholder for future implementation)
        # For elemental: damage = damage * (1 + (int + wis) / 200) * elemental_affinity_multiplier
        
        return {
            "damage_type": "elemental",
            "element": self.element_type,
            "amount": max(0.0, damage),
            "node_type": self.node_type,
        }


class SkillDamageNode(DamageNode):
    """
    Damage node that executes a skill.
    
    Attributes:
        skill: Skill object to execute
    """
    
    def __init__(
        self,
        node_type: str,
        execution_probability: float,
        skill: Any,
    ):
        """
        Initialize a skill damage node.
        
        Args:
            node_type: Type of node
            execution_probability: Probability of execution
            skill: Skill object to execute
        """
        super().__init__(node_type, execution_probability)
        self.skill = skill
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the skill.
        
        Args:
            character: Character using the weapon
            target: Target character
            
        Returns:
            Dictionary with skill execution results
        """
        if self.skill and hasattr(self.skill, "execute"):
            return self.skill.execute(character, target)
        
        return {
            "damage_type": "skill",
            "skill": self.skill.name if hasattr(self.skill, "name") else "unknown",
            "node_type": self.node_type,
        }


class SpellDamageNode(DamageNode):
    """
    Damage node that executes a spell.
    
    Attributes:
        spell: Spell object to execute
    """
    
    def __init__(
        self,
        node_type: str,
        execution_probability: float,
        spell: Any,
    ):
        """
        Initialize a spell damage node.
        
        Args:
            node_type: Type of node
            execution_probability: Probability of execution
            spell: Spell object to execute
        """
        super().__init__(node_type, execution_probability)
        self.spell = spell
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the spell.
        
        Args:
            character: Character using the weapon
            target: Target character
            
        Returns:
            Dictionary with spell execution results
        """
        if self.spell and hasattr(self.spell, "execute"):
            return self.spell.execute(character, target)
        
        return {
            "damage_type": "spell",
            "spell": self.spell.name if hasattr(self.spell, "name") else "unknown",
            "node_type": self.node_type,
        }


class ProcessDamageNode(DamageNode):
    """
    Damage node that executes a process (unique function).
    
    Attributes:
        process: Process object to execute
    """
    
    def __init__(
        self,
        node_type: str,
        execution_probability: float,
        process: Any,
    ):
        """
        Initialize a process damage node.
        
        Args:
            node_type: Type of node
            execution_probability: Probability of execution
            process: Process object to execute
        """
        super().__init__(node_type, execution_probability)
        self.process = process
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the process.
        
        Args:
            character: Character using the weapon
            target: Target character or object
            
        Returns:
            Dictionary with process execution results
        """
        if self.process and hasattr(self.process, "execute"):
            return self.process.execute(character, target)
        
        return {
            "damage_type": "process",
            "process": self.process.name if hasattr(self.process, "name") else "unknown",
            "node_type": self.node_type,
        }

