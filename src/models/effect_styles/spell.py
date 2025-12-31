"""Spell effect style for spell/magic effects."""

from typing import Dict, Any
from src.models.effect_styles.base import EffectStyle
from src.models.effectors.base import Effector
from src.models.effectors.damage import DamageEffector
from src.utils.constants import DAMAGE_SUBTYPE_ELEMENTAL


class SpellEffectStyle(EffectStyle):
    """
    Spell effect style for magical/spell effects.
    
    Spell styles typically use damage effectors with elemental damage subtype.
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
        Initialize a spell effect style.
        
        Args:
            name: Style name (e.g., "Lightning", "Fireball")
            subtype: Subtype identifier (e.g., "lightning", "fire")
            effector: Effector instance (typically DamageEffector with elemental damage)
            description: Description of the style
            process_verb: Verb for process messages
            execution_probability: Probability of execution
        """
        super().__init__(
            name=name,
            style_type=self.STYLE_TYPE_SPELL,
            subtype=subtype,
            effector=effector,
            description=description,
            process_verb=process_verb or subtype,
            execution_probability=execution_probability,
        )
        
        # Validate that effector is appropriate for spell style
        if isinstance(effector, DamageEffector):
            if effector.damage_subtype != DAMAGE_SUBTYPE_ELEMENTAL:
                raise ValueError(
                    f"SpellEffectStyle typically uses elemental damage effector, "
                    f"got {effector.damage_subtype}"
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
    def from_config(cls, config: Dict[str, Any]) -> 'SpellEffectStyle':
        """Create style from configuration dictionary."""
        from src.models.effectors import DamageEffector
        
        effector_config = config.get("effector", {})
        # Ensure distribution_parameters are included if not in effector config
        if "distribution_parameters" not in effector_config and "distribution_parameters" in config:
            effector_config["distribution_parameters"] = config["distribution_parameters"]
        
        effector = DamageEffector.from_config(effector_config)
        
        return cls(
            name=config["name"],
            subtype=config["subtype"],
            effector=effector,
            description=config.get("description", ""),
            process_verb=config.get("process_verb", config["subtype"]),
            execution_probability=config.get("execution_probability", 1.0),
        )

