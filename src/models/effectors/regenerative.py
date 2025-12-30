"""Regenerative effector classes."""

from typing import Dict, Any, Optional
from src.models.effectors.base import Effector
from src.utils.common.distributions import DistributionFunction


class RegenerativeEffector(Effector):
    """
    Regenerative effector that applies positive effects (healing, restoration, etc.).
    
    Similar to damage effector but with positive impact. Can restore health,
    mana, stamina, or other attributes.
    
    Attributes:
        attribute_type: Type of attribute being restored (health, mana, stamina, etc.)
        restoration_model: Distribution function that returns restoration value
        base_restoration: Base restoration value
    """
    
    def __init__(
        self,
        effector_name: str,
        attribute_type: str,
        restoration_model: DistributionFunction,
        base_restoration: float = 0.0,
    ):
        """
        Initialize a regenerative effector.
        
        Args:
            effector_name: Name/identifier for this effector
            attribute_type: Type of attribute being restored
            restoration_model: Function that returns restoration value when called
            base_restoration: Base restoration value
        """
        super().__init__(
            effector_type="regenerative",
            effector_name=effector_name,
        )
        self.attribute_type = attribute_type
        self.restoration_model = restoration_model
        self.base_restoration = base_restoration
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute restoration calculation.
        
        Args:
            character: Character using the item/skill
            target: Target character (usually same as character for self-heal)
            
        Returns:
            Dictionary with restoration type, amount, and other effects
        """
        # Sample restoration from distribution model
        restoration = self.restoration_model()
        
        # Apply character stat modifiers (placeholder for future implementation)
        # restoration = restoration * (1 + character.get_stat("wis") / 100)
        
        return {
            "effector_type": "regenerative",
            "effector_name": self.effector_name,
            "attribute_type": self.attribute_type,
            "amount": max(0.0, restoration),
        }
    
    def to_config(self) -> Dict[str, Any]:
        """Convert effector to configuration dictionary."""
        return {
            "effector_type": self.effector_type,
            "effector_name": self.effector_name,
            "attribute_type": self.attribute_type,
            "base_restoration": self.base_restoration,
            # distribution_parameters would be stored separately
        }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'RegenerativeEffector':
        """Create effector from configuration dictionary."""
        from src.utils.common.distributions import create_distribution_function
        
        distribution_params = config.get("distribution_parameters", {})
        restoration_model = create_distribution_function(distribution_params)
        
        return cls(
            effector_name=config["effector_name"],
            attribute_type=config["attribute_type"],
            restoration_model=restoration_model,
            base_restoration=config.get("base_restoration", 0.0),
        )
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get tunable parameters."""
        params = super().get_parameters()
        params.update({
            "attribute_type": self.attribute_type,
            "base_restoration": self.base_restoration,
        })
        return params

