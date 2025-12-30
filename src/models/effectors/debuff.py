"""Debuff effector classes."""

from typing import Dict, Any, List, Optional
from src.models.effectors.base import Effector
from src.utils.common.distributions import DistributionFunction
from src.utils.constants import CORE_STATS, AUXILIARY_STATS


class DebuffEffector(Effector):
    """
    Debuff effector that decreases attributes with a distribution model.
    
    Similar to BuffEffector but with negative impact.
    
    Attributes:
        affected_attributes: List of attribute names being debuffed
        debuff_model: Distribution function that returns debuff magnitude
        base_debuff: Base debuff value
        duration: Duration of the debuff in turns/seconds
        stackable: Whether multiple instances can stack
    """
    
    def __init__(
        self,
        effector_name: str,
        affected_attributes: List[str],
        debuff_model: DistributionFunction,
        base_debuff: float = 0.0,
        duration: Optional[float] = None,
        stackable: bool = False,
    ):
        """
        Initialize a debuff effector.
        
        Args:
            effector_name: Name/identifier for this effector
            affected_attributes: List of attribute names being debuffed
            debuff_model: Function that returns debuff magnitude when called
            base_debuff: Base debuff value
            duration: Duration of the debuff (None for permanent)
            stackable: Whether multiple instances can stack
        """
        super().__init__(
            effector_type="debuff",
            effector_name=effector_name,
        )
        
        # Validate attributes
        all_attributes = CORE_STATS + AUXILIARY_STATS
        for attr in affected_attributes:
            if attr not in all_attributes:
                raise ValueError(f"Invalid attribute: {attr}")
        
        self.affected_attributes = affected_attributes
        self.debuff_model = debuff_model
        self.base_debuff = base_debuff
        self.duration = duration
        self.stackable = stackable
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute debuff application.
        
        Args:
            character: Character using the item/skill
            target: Target character to debuff
            
        Returns:
            Dictionary with debuff application results
        """
        # Sample debuff magnitude from distribution model
        debuff_magnitude = self.debuff_model()
        
        return {
            "effector_type": "debuff",
            "effector_name": self.effector_name,
            "affected_attributes": self.affected_attributes,
            "magnitude": max(0.0, debuff_magnitude),
            "duration": self.duration,
            "stackable": self.stackable,
        }
    
    def to_config(self) -> Dict[str, Any]:
        """Convert effector to configuration dictionary."""
        config = {
            "effector_type": self.effector_type,
            "effector_name": self.effector_name,
            "affected_attributes": self.affected_attributes,
            "base_debuff": self.base_debuff,
            "stackable": self.stackable,
        }
        if self.duration is not None:
            config["duration"] = self.duration
        return config
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'DebuffEffector':
        """Create effector from configuration dictionary."""
        from src.utils.common.distributions import create_distribution_function
        
        distribution_params = config.get("distribution_parameters", {})
        debuff_model = create_distribution_function(distribution_params)
        
        return cls(
            effector_name=config["effector_name"],
            affected_attributes=config["affected_attributes"],
            debuff_model=debuff_model,
            base_debuff=config.get("base_debuff", 0.0),
            duration=config.get("duration"),
            stackable=config.get("stackable", False),
        )
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get tunable parameters."""
        params = super().get_parameters()
        params.update({
            "affected_attributes": self.affected_attributes,
            "base_debuff": self.base_debuff,
            "stackable": self.stackable,
        })
        if self.duration is not None:
            params["duration"] = self.duration
        return params

