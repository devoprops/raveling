"""Functional node classes for item effects (damage, buffs, debuffs, skills, spells, processes)."""

from typing import Dict, Any, Optional, Callable, Union
from abc import ABC, abstractmethod
from src.utils.constants import (
    FUNCTIONAL_NODE_TYPES,
    FUNCTIONAL_NODE_DAMAGE,
    FUNCTIONAL_NODE_BUFF,
    FUNCTIONAL_NODE_DEBUFF,
    FUNCTIONAL_NODE_SKILL,
    FUNCTIONAL_NODE_SPELL,
    FUNCTIONAL_NODE_PROCESS,
    FUNCTIONAL_NODE_CLASSES,
    FUNCTIONAL_NODE_CLASS_INNATE,
    FUNCTIONAL_NODE_CLASS_PRIMARY,
    FUNCTIONAL_NODE_CLASS_AUXILIARY,
    DAMAGE_SUBTYPES,
    DAMAGE_SUBTYPE_PHYSICAL,
    DAMAGE_SUBTYPE_ELEMENTAL,
    ELEMENTS,
)
from src.utils.common.distributions import DistributionFunction


class FunctionalNode(ABC):
    """
    Base class for functional nodes in items (weapons, wearables, etc.).
    
    Functional nodes represent potential effects that can be triggered when an item
    is used. Nodes are evaluated independently based on their execution probability.
    Not all nodes apply damage - they can apply buffs, debuffs, or other effects.
    
    Attributes:
        node_type: Type of node (damage, buff, debuff, skill, spell, process)
        node_class: Class of node (innate, primary, auxiliary) - determines when/how active
        execution_probability: Probability of this node executing (0.0 to 1.0)
    """
    
    def __init__(
        self,
        node_type: str,
        node_class: str,
        execution_probability: float,
    ):
        """
        Initialize a functional node.
        
        Args:
            node_type: Type of node (must be in FUNCTIONAL_NODE_TYPES)
            node_class: Class of node (innate, primary, auxiliary)
            execution_probability: Probability of execution (0.0 to 1.0)
        """
        if node_type not in FUNCTIONAL_NODE_TYPES:
            raise ValueError(f"Invalid node_type: {node_type}")
        self.node_type = node_type
        
        if node_class not in FUNCTIONAL_NODE_CLASSES:
            raise ValueError(f"Invalid node_class: {node_class}")
        self.node_class = node_class
        
        if not 0.0 <= execution_probability <= 1.0:
            raise ValueError("execution_probability must be between 0.0 and 1.0")
        self.execution_probability = execution_probability
    
    @abstractmethod
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the functional node and return results.
        
        Args:
            character: Character using the item
            target: Target character or object
            
        Returns:
            Dictionary containing effect results (varies by node type)
        """
        pass
    
    def is_active(self, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if this node is active based on its class and context.
        
        Args:
            context: Optional context dictionary for determining activity
            
        Returns:
            True if node is active, False otherwise
        """
        # Innate nodes are always active
        if self.node_class == FUNCTIONAL_NODE_CLASS_INNATE:
            return True
        
        # Primary nodes are active by default (can be overridden by context)
        if self.node_class == FUNCTIONAL_NODE_CLASS_PRIMARY:
            if context and "primary_active" in context:
                return context["primary_active"]
            return True
        
        # Auxiliary nodes require activation (e.g., from slots)
        if self.node_class == FUNCTIONAL_NODE_CLASS_AUXILIARY:
            if context and "auxiliary_active" in context:
                return context.get("auxiliary_active", False)
            return False
        
        return False


class DamageNode(FunctionalNode):
    """
    Base class for damage functional nodes.
    
    Damage nodes apply damage of a specific subtype (physical or elemental).
    """
    
    def __init__(
        self,
        node_class: str,
        execution_probability: float,
        damage_subtype: str,
        damage_model: DistributionFunction,
        base_damage: float = 0.0,
    ):
        """
        Initialize a damage node.
        
        Args:
            node_class: Class of node (innate, primary, auxiliary)
            execution_probability: Probability of execution
            damage_subtype: Subtype of damage (physical or elemental)
            damage_model: Function that returns damage value when called
            base_damage: Base damage value (if needed by damage_model)
        """
        super().__init__(
            node_type=FUNCTIONAL_NODE_DAMAGE,
            node_class=node_class,
            execution_probability=execution_probability,
        )
        
        if damage_subtype not in DAMAGE_SUBTYPES:
            raise ValueError(f"Invalid damage_subtype: {damage_subtype}")
        self.damage_subtype = damage_subtype
        
        self.damage_model = damage_model
        self.base_damage = base_damage
    
    @abstractmethod
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """Execute damage calculation - implemented by subclasses."""
        pass


class PhysicalDamageNode(DamageNode):
    """
    Physical damage node that applies physical damage using a distribution model.
    """
    
    def __init__(
        self,
        node_class: str,
        execution_probability: float,
        damage_model: DistributionFunction,
        base_damage: float = 0.0,
    ):
        """
        Initialize a physical damage node.
        
        Args:
            node_class: Class of node (innate, primary, auxiliary)
            execution_probability: Probability of execution
            damage_model: Function that returns damage value when called
            base_damage: Base damage value (if needed by damage_model)
        """
        super().__init__(
            node_class=node_class,
            execution_probability=execution_probability,
            damage_subtype=DAMAGE_SUBTYPE_PHYSICAL,
            damage_model=damage_model,
            base_damage=base_damage,
        )
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute physical damage calculation.
        
        Args:
            character: Character using the item
            target: Target character
            
        Returns:
            Dictionary with damage type, amount, and other effects
        """
        # Sample damage from distribution model
        damage = self.damage_model()
        
        # Apply character stat modifiers (placeholder for future implementation)
        # damage = damage * (1 + character.get_stat("str") / 100) * skill_multiplier
        
        return {
            "node_type": FUNCTIONAL_NODE_DAMAGE,
            "damage_subtype": DAMAGE_SUBTYPE_PHYSICAL,
            "amount": max(0.0, damage),
            "node_class": self.node_class,
        }


class ElementalDamageNode(DamageNode):
    """
    Elemental damage node that applies elemental damage.
    
    Attributes:
        element_type: Type of element (fire, water, etc.)
    """
    
    def __init__(
        self,
        node_class: str,
        execution_probability: float,
        element_type: str,
        damage_model: DistributionFunction,
        base_damage: float = 0.0,
    ):
        """
        Initialize an elemental damage node.
        
        Args:
            node_class: Class of node (innate, primary, auxiliary)
            execution_probability: Probability of execution
            element_type: Type of element (must be in ELEMENTS)
            damage_model: Function that returns damage value when called
            base_damage: Base damage value
        """
        super().__init__(
            node_class=node_class,
            execution_probability=execution_probability,
            damage_subtype=DAMAGE_SUBTYPE_ELEMENTAL,
            damage_model=damage_model,
            base_damage=base_damage,
        )
        
        if element_type not in ELEMENTS:
            raise ValueError(f"Invalid element_type: {element_type}")
        self.element_type = element_type
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute elemental damage calculation.
        
        Args:
            character: Character using the item
            target: Target character
            
        Returns:
            Dictionary with damage type, element, amount, and other effects
        """
        # Sample damage from distribution model
        damage = self.damage_model()
        
        # Apply character stat modifiers (placeholder for future implementation)
        # For elemental: damage = damage * (1 + (int + wis) / 200) * elemental_affinity_multiplier
        
        return {
            "node_type": FUNCTIONAL_NODE_DAMAGE,
            "damage_subtype": DAMAGE_SUBTYPE_ELEMENTAL,
            "element": self.element_type,
            "amount": max(0.0, damage),
            "node_class": self.node_class,
        }


class BuffNode(FunctionalNode):
    """
    Functional node that applies a buff effect.
    
    Attributes:
        buff_effect: Buff effect object or dictionary
    """
    
    def __init__(
        self,
        node_class: str,
        execution_probability: float,
        buff_effect: Any,
    ):
        """
        Initialize a buff node.
        
        Args:
            node_class: Class of node (innate, primary, auxiliary)
            execution_probability: Probability of execution
            buff_effect: Buff effect object or dictionary
        """
        super().__init__(
            node_type=FUNCTIONAL_NODE_BUFF,
            node_class=node_class,
            execution_probability=execution_probability,
        )
        self.buff_effect = buff_effect
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the buff effect.
        
        Args:
            character: Character using the item
            target: Target character (usually same as character for self-buff)
            
        Returns:
            Dictionary with buff application results
        """
        # If buff_effect is a skill, execute it
        if hasattr(self.buff_effect, "execute"):
            result = self.buff_effect.execute(character, target)
            result["node_type"] = FUNCTIONAL_NODE_BUFF
            result["node_class"] = self.node_class
            return result
        
        # Otherwise, return buff information
        return {
            "node_type": FUNCTIONAL_NODE_BUFF,
            "node_class": self.node_class,
            "buff_effect": self.buff_effect,
        }


class DebuffNode(FunctionalNode):
    """
    Functional node that applies a debuff effect.
    
    Attributes:
        debuff_effect: Debuff effect object or dictionary
    """
    
    def __init__(
        self,
        node_class: str,
        execution_probability: float,
        debuff_effect: Any,
    ):
        """
        Initialize a debuff node.
        
        Args:
            node_class: Class of node (innate, primary, auxiliary)
            execution_probability: Probability of execution
            debuff_effect: Debuff effect object or dictionary
        """
        super().__init__(
            node_type=FUNCTIONAL_NODE_DEBUFF,
            node_class=node_class,
            execution_probability=execution_probability,
        )
        self.debuff_effect = debuff_effect
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the debuff effect.
        
        Args:
            character: Character using the item
            target: Target character to debuff
            
        Returns:
            Dictionary with debuff application results
        """
        # If debuff_effect is a skill, execute it
        if hasattr(self.debuff_effect, "execute"):
            result = self.debuff_effect.execute(character, target)
            result["node_type"] = FUNCTIONAL_NODE_DEBUFF
            result["node_class"] = self.node_class
            return result
        
        # Otherwise, return debuff information
        return {
            "node_type": FUNCTIONAL_NODE_DEBUFF,
            "node_class": self.node_class,
            "debuff_effect": self.debuff_effect,
        }


class SkillNode(FunctionalNode):
    """
    Functional node that executes a skill.
    
    Attributes:
        skill: Skill object to execute
    """
    
    def __init__(
        self,
        node_class: str,
        execution_probability: float,
        skill: Any,
    ):
        """
        Initialize a skill node.
        
        Args:
            node_class: Class of node (innate, primary, auxiliary)
            execution_probability: Probability of execution
            skill: Skill object to execute
        """
        super().__init__(
            node_type=FUNCTIONAL_NODE_SKILL,
            node_class=node_class,
            execution_probability=execution_probability,
        )
        self.skill = skill
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the skill.
        
        Args:
            character: Character using the item
            target: Target character
            
        Returns:
            Dictionary with skill execution results
        """
        if self.skill and hasattr(self.skill, "execute"):
            result = self.skill.execute(character, target)
            result["node_type"] = FUNCTIONAL_NODE_SKILL
            result["node_class"] = self.node_class
            return result
        
        return {
            "node_type": FUNCTIONAL_NODE_SKILL,
            "node_class": self.node_class,
            "skill": self.skill.name if hasattr(self.skill, "name") else "unknown",
        }


class SpellNode(FunctionalNode):
    """
    Functional node that executes a spell.
    
    Attributes:
        spell: Spell object to execute
    """
    
    def __init__(
        self,
        node_class: str,
        execution_probability: float,
        spell: Any,
    ):
        """
        Initialize a spell node.
        
        Args:
            node_class: Class of node (innate, primary, auxiliary)
            execution_probability: Probability of execution
            spell: Spell object to execute
        """
        super().__init__(
            node_type=FUNCTIONAL_NODE_SPELL,
            node_class=node_class,
            execution_probability=execution_probability,
        )
        self.spell = spell
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the spell.
        
        Args:
            character: Character using the item
            target: Target character
            
        Returns:
            Dictionary with spell execution results
        """
        if self.spell and hasattr(self.spell, "execute"):
            result = self.spell.execute(character, target)
            result["node_type"] = FUNCTIONAL_NODE_SPELL
            result["node_class"] = self.node_class
            return result
        
        return {
            "node_type": FUNCTIONAL_NODE_SPELL,
            "node_class": self.node_class,
            "spell": self.spell.name if hasattr(self.spell, "name") else "unknown",
        }


class ProcessNode(FunctionalNode):
    """
    Functional node that executes a process (unique function).
    
    Attributes:
        process: Process object to execute
    """
    
    def __init__(
        self,
        node_class: str,
        execution_probability: float,
        process: Any,
    ):
        """
        Initialize a process node.
        
        Args:
            node_class: Class of node (innate, primary, auxiliary)
            execution_probability: Probability of execution
            process: Process object to execute
        """
        super().__init__(
            node_type=FUNCTIONAL_NODE_PROCESS,
            node_class=node_class,
            execution_probability=execution_probability,
        )
        self.process = process
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the process.
        
        Args:
            character: Character using the item
            target: Target character or object
            
        Returns:
            Dictionary with process execution results
        """
        if self.process and hasattr(self.process, "execute"):
            result = self.process.execute(character, target)
            result["node_type"] = FUNCTIONAL_NODE_PROCESS
            result["node_class"] = self.node_class
            return result
        
        return {
            "node_type": FUNCTIONAL_NODE_PROCESS,
            "node_class": self.node_class,
            "process": self.process.name if hasattr(self.process, "name") else "unknown",
        }

