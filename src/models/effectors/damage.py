"""Damage effector classes."""

from typing import Dict, Any, Optional
from src.models.effectors.base import Effector
from src.utils.constants import DAMAGE_SUBTYPES, DAMAGE_SUBTYPE_PHYSICAL, DAMAGE_SUBTYPE_ELEMENTAL, ELEMENTS
from src.utils.common.distributions import DistributionFunction


class DamageEffector(Effector):
    """
    Damage effector that applies damage using a distribution model.
    
    Attributes:
        damage_subtype: Subtype of damage (physical or elemental)
        element_type: Type of element (if elemental damage, None otherwise)
        damage_model: Distribution function that returns damage value
        base_damage: Base damage value
    """
    
    def __init__(
        self,
        effector_name: str,
        damage_subtype: str,
        damage_model: DistributionFunction,
        base_damage: float = 0.0,
        element_type: Optional[str] = None,
    ):
        """
        Initialize a damage effector.
        
        Args:
            effector_name: Name/identifier for this effector
            damage_subtype: Subtype of damage (physical or elemental)
            damage_model: Function that returns damage value when called
            base_damage: Base damage value
            element_type: Type of element (required if damage_subtype is elemental)
        """
        super().__init__(
            effector_type="damage",
            effector_name=effector_name,
        )
        
        if damage_subtype not in DAMAGE_SUBTYPES:
            raise ValueError(f"Invalid damage_subtype: {damage_subtype}")
        self.damage_subtype = damage_subtype
        
        if damage_subtype == DAMAGE_SUBTYPE_ELEMENTAL:
            if element_type is None:
                raise ValueError("element_type is required for elemental damage")
            if element_type not in ELEMENTS:
                raise ValueError(f"Invalid element_type: {element_type}")
            self.element_type = element_type
        else:
            self.element_type = None
        
        self.damage_model = damage_model
        self.base_damage = base_damage
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute damage calculation.
        
        Args:
            character: Character using the item/skill
            target: Target character
            
        Returns:
            Dictionary with damage type, amount, and other effects
        """
        # Sample damage from distribution model
        damage = self.damage_model()
        
        # Apply character stat modifiers (placeholder for future implementation)
        # For physical: damage = damage * (1 + character.get_stat("str") / 100)
        # For elemental: damage = damage * (1 + (int + wis) / 200)
        
        result = {
            "effector_type": "damage",
            "effector_name": self.effector_name,
            "damage_subtype": self.damage_subtype,
            "amount": max(0.0, damage),
        }
        
        if self.damage_subtype == DAMAGE_SUBTYPE_ELEMENTAL:
            result["element"] = self.element_type
        
        return result
    
    def to_config(self) -> Dict[str, Any]:
        """Convert effector to configuration dictionary."""
        config = {
            "effector_type": self.effector_type,
            "effector_name": self.effector_name,
            "damage_subtype": self.damage_subtype,
            "base_damage": self.base_damage,
        }
        
        if self.damage_subtype == DAMAGE_SUBTYPE_ELEMENTAL:
            config["element_type"] = self.element_type
        
        # Include distribution parameters
        # Note: DistributionFunction serialization would need to be handled separately
        # For now, we assume distribution_parameters are stored separately
        return config
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'DamageEffector':
        """Create effector from configuration dictionary."""
        # Distribution model would need to be reconstructed from distribution_parameters
        # This is a placeholder - actual implementation would need distribution factory
        from src.utils.common.distributions import create_distribution_function
        
        distribution_params = config.get("distribution_parameters", {})
        damage_model = create_distribution_function(distribution_params)
        
        return cls(
            effector_name=config["effector_name"],
            damage_subtype=config["damage_subtype"],
            damage_model=damage_model,
            base_damage=config.get("base_damage", 0.0),
            element_type=config.get("element_type"),
        )
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get tunable parameters."""
        params = super().get_parameters()
        params.update({
            "damage_subtype": self.damage_subtype,
            "base_damage": self.base_damage,
        })
        if self.element_type:
            params["element_type"] = self.element_type
        return params

