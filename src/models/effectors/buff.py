"""Buff effector classes."""

from typing import Dict, Any, List, Optional
from src.models.effectors.base import Effector
from src.utils.common.distributions import DistributionFunction
from src.utils.constants import CORE_STATS, AUXILIARY_STATS


class BuffEffector(Effector):
    """
    Buff effector that increases attributes with a distribution model.
    
    Attributes:
        affected_attributes: List of attribute names being buffed
        buff_model: Distribution function that returns buff magnitude
        base_buff: Base buff value
        duration: Duration of the buff in turns/seconds
        stackable: Whether multiple instances can stack
    """
    
    def __init__(
        self,
        effector_name: str,
        affected_attributes: List[str],
        buff_model: DistributionFunction,
        base_buff: float = 0.0,
        duration: Optional[float] = None,
        stackable: bool = False,
    ):
        """
        Initialize a buff effector.
        
        Args:
            effector_name: Name/identifier for this effector
            affected_attributes: List of attribute names being buffed
            buff_model: Function that returns buff magnitude when called
            base_buff: Base buff value
            duration: Duration of the buff (None for permanent)
            stackable: Whether multiple instances can stack
        """
        super().__init__(
            effector_type="buff",
            effector_name=effector_name,
        )
        
        # Validate attributes
        all_attributes = CORE_STATS + AUXILIARY_STATS
        for attr in affected_attributes:
            if attr not in all_attributes:
                raise ValueError(f"Invalid attribute: {attr}")
        
        self.affected_attributes = affected_attributes
        self.buff_model = buff_model
        self.base_buff = base_buff
        self.duration = duration
        self.stackable = stackable
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute buff application.
        
        Args:
            character: Character using the item/skill
            target: Target character (usually same as character for self-buff)
            
        Returns:
            Dictionary with buff application results
        """
        # Sample buff magnitude from distribution model
        buff_magnitude = self.buff_model()
        
        return {
            "effector_type": "buff",
            "effector_name": self.effector_name,
            "affected_attributes": self.affected_attributes,
            "magnitude": max(0.0, buff_magnitude),
            "duration": self.duration,
            "stackable": self.stackable,
        }
    
    def to_config(self) -> Dict[str, Any]:
        """Convert effector to configuration dictionary."""
        config = {
            "effector_type": self.effector_type,
            "effector_name": self.effector_name,
            "affected_attributes": self.affected_attributes,
            "base_buff": self.base_buff,
            "stackable": self.stackable,
        }
        if self.duration is not None:
            config["duration"] = self.duration
        return config
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'BuffEffector':
        """Create effector from configuration dictionary."""
        from src.utils.common.distributions import create_distribution_function
        
        distribution_params = config.get("distribution_parameters", {})
        buff_model = create_distribution_function(distribution_params)
        
        return cls(
            effector_name=config["effector_name"],
            affected_attributes=config["affected_attributes"],
            buff_model=buff_model,
            base_buff=config.get("base_buff", 0.0),
            duration=config.get("duration"),
            stackable=config.get("stackable", False),
        )
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get tunable parameters."""
        params = super().get_parameters()
        params.update({
            "affected_attributes": self.affected_attributes,
            "base_buff": self.base_buff,
            "stackable": self.stackable,
        })
        if self.duration is not None:
            params["duration"] = self.duration
        return params

