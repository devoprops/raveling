"""Base EffectStyle class for wrapping effectors with style metadata."""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from src.models.effectors.base import Effector


class EffectStyle(ABC):
    """
    Base class for effect styles.
    
    EffectStyles wrap Effectors with additional metadata like name, subtype,
    description, and process_verb. They provide a higher-level abstraction
    for configuring weapon/item effects.
    
    Attributes:
        name: Style name (e.g., "Slash", "Lightning")
        style_type: Type of style (Physical, Spell, Buff, Debuff, Regen, Process)
        subtype: Subtype identifier (e.g., "slash", "thrust" for Physical)
        description: Description of the style
        effector: Reference to the effector instance
        process_verb: Verb for process messages (e.g., "slash", "thrust", "kick")
        execution_probability: Probability of execution (0.0 to 1.0, default 1.0)
    """
    
    STYLE_TYPE_PHYSICAL = "Physical"
    STYLE_TYPE_SPELL = "Spell"
    STYLE_TYPE_BUFF = "Buff"
    STYLE_TYPE_DEBUFF = "Debuff"
    STYLE_TYPE_REGEN = "Regen"
    STYLE_TYPE_PROCESS = "Process"
    
    STYLE_TYPES = [
        STYLE_TYPE_PHYSICAL,
        STYLE_TYPE_SPELL,
        STYLE_TYPE_BUFF,
        STYLE_TYPE_DEBUFF,
        STYLE_TYPE_REGEN,
        STYLE_TYPE_PROCESS,
    ]
    
    def __init__(
        self,
        name: str,
        style_type: str,
        subtype: str,
        effector: Effector,
        description: str = "",
        process_verb: str = "",
        execution_probability: float = 1.0,
    ):
        """
        Initialize an effect style.
        
        Args:
            name: Style name
            style_type: Type of style (must be in STYLE_TYPES)
            subtype: Subtype identifier
            effector: Effector instance
            description: Description of the style
            process_verb: Verb for process messages
            execution_probability: Probability of execution (0.0 to 1.0)
        """
        if style_type not in self.STYLE_TYPES:
            raise ValueError(f"Invalid style_type: {style_type}. Must be one of {self.STYLE_TYPES}")
        
        if not 0.0 <= execution_probability <= 1.0:
            raise ValueError("execution_probability must be between 0.0 and 1.0")
        
        self.name = name
        self.style_type = style_type
        self.subtype = subtype
        self.effector = effector
        self.description = description
        self.process_verb = process_verb or subtype  # Default to subtype if not provided
        self.execution_probability = execution_probability
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the style's effector.
        
        Args:
            character: Character using the item/skill
            target: Target character or object
            
        Returns:
            Dictionary containing effect results
        """
        return self.effector.execute(character, target)
    
    @abstractmethod
    def to_config(self) -> Dict[str, Any]:
        """
        Convert style to configuration dictionary.
        
        Returns:
            Dictionary representation of style configuration
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_config(cls, config: Dict[str, Any]) -> 'EffectStyle':
        """
        Create style instance from configuration dictionary.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            EffectStyle instance
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about this style.
        
        Returns:
            Dictionary with style information
        """
        return {
            "name": self.name,
            "style_type": self.style_type,
            "subtype": self.subtype,
            "description": self.description,
            "process_verb": self.process_verb,
            "execution_probability": self.execution_probability,
            "effector_type": self.effector.effector_type,
            "effector_name": self.effector.effector_name,
        }
    
    @staticmethod
    def from_config(config: Dict[str, Any]) -> 'EffectStyle':
        """
        Factory method to create EffectStyle from configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            EffectStyle instance of appropriate subclass
        """
        style_type = config.get("style_type", "")
        
        if style_type == EffectStyle.STYLE_TYPE_PHYSICAL:
            from src.models.effect_styles.physical import PhysicalEffectStyle
            return PhysicalEffectStyle.from_config(config)
        elif style_type == EffectStyle.STYLE_TYPE_SPELL:
            from src.models.effect_styles.spell import SpellEffectStyle
            return SpellEffectStyle.from_config(config)
        elif style_type == EffectStyle.STYLE_TYPE_BUFF:
            from src.models.effect_styles.buff import BuffEffectStyle
            return BuffEffectStyle.from_config(config)
        elif style_type == EffectStyle.STYLE_TYPE_DEBUFF:
            from src.models.effect_styles.debuff import DebuffEffectStyle
            return DebuffEffectStyle.from_config(config)
        elif style_type == EffectStyle.STYLE_TYPE_REGEN:
            from src.models.effect_styles.regen import RegenEffectStyle
            return RegenEffectStyle.from_config(config)
        elif style_type == EffectStyle.STYLE_TYPE_PROCESS:
            from src.models.effect_styles.process import ProcessEffectStyle
            return ProcessEffectStyle.from_config(config)
        else:
            raise ValueError(f"Unknown style_type: {style_type}")

