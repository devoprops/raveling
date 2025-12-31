"""Buff effect style for buff effects."""

from typing import Dict, Any
from src.models.effect_styles.base import EffectStyle
from src.models.effectors.base import Effector
from src.models.effectors.buff import BuffEffector


class BuffEffectStyle(EffectStyle):
    """
    Buff effect style for buff effects.
    
    Buff styles use BuffEffector instances.
    """
    
    def __init__(
        self,
        name: str,
        subtype: str,
        effector: Effector,
        description: str = "",
        process_verb: str = "",
        execution_probability: float = 1.0,
    ):
        """
        Initialize a buff effect style.
        
        Args:
            name: Style name (e.g., "Strength Boost")
            subtype: Subtype identifier
            effector: BuffEffector instance
            description: Description of the style
            process_verb: Verb for process messages
            execution_probability: Probability of execution
        """
        super().__init__(
            name=name,
            style_type=self.STYLE_TYPE_BUFF,
            subtype=subtype,
            effector=effector,
            description=description,
            process_verb=process_verb or subtype,
            execution_probability=execution_probability,
        )
    
    def to_config(self) -> Dict[str, Any]:
        """Convert style to configuration dictionary."""
        return {
            "name": self.name,
            "style_type": self.style_type,
            "subtype": self.subtype,
            "description": self.description,
            "process_verb": self.process_verb,
            "execution_probability": self.execution_probability,
            "effector": self.effector.to_config(),
        }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'BuffEffectStyle':
        """Create style from configuration dictionary."""
        from src.models.effectors import BuffEffector
        
        effector_config = config.get("effector", {})
        # Ensure distribution_parameters are included if not in effector config
        if "distribution_parameters" not in effector_config and "distribution_parameters" in config:
            effector_config["distribution_parameters"] = config["distribution_parameters"]
        
        effector = BuffEffector.from_config(effector_config)
        
        return cls(
            name=config["name"],
            subtype=config["subtype"],
            effector=effector,
            description=config.get("description", ""),
            process_verb=config.get("process_verb", config["subtype"]),
            execution_probability=config.get("execution_probability", 1.0),
        )

