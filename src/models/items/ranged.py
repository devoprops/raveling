"""Ranged weapon subclasses."""

from typing import Dict, Any, Optional
from src.models.items.weapon import Weapon
from src.models.items.damage_node import DamageNode
from src.utils.constants import RANGED_BOW, RANGED_THROWABLE


class Bow(Weapon):
    """
    Bow ranged weapon.
    
    Attributes:
        range: Maximum effective range
        ammo_type: Type of ammunition required
        draw_strength: Draw strength required
    """
    
    def __init__(
        self,
        name: str,
        short_desc: str,
        long_desc: str,
        weight: float,
        size: float,
        material: str,
        damage_nodes: list[DamageNode],
        range: float,
        ammo_type: str,
        draw_strength: float,
        restrictions: Dict[str, Any] = None,
    ):
        """
        Initialize a bow.
        
        Args:
            name: Weapon name
            short_desc: Short description
            long_desc: Long description
            weight: Weight of the weapon
            size: Size of the weapon
            material: Material the weapon is made from
            damage_nodes: List of DamageNode instances
            range: Maximum effective range
            ammo_type: Type of ammunition required
            draw_strength: Draw strength required
            restrictions: Optional dictionary of restrictions
        """
        super().__init__(
            name=name,
            short_desc=short_desc,
            long_desc=long_desc,
            weight=weight,
            size=size,
            material=material,
            damage_nodes=damage_nodes,
            restrictions=restrictions,
        )
        self.range = range
        self.ammo_type = ammo_type
        self.draw_strength = draw_strength
        self.weapon_subtype = RANGED_BOW
    
    def calculate_range_modifier(self, distance: float) -> float:
        """
        Calculate damage/accuracy modifier based on distance.
        
        Args:
            distance: Distance to target
            
        Returns:
            Modifier value (1.0 = no change, <1.0 = reduced, >1.0 = increased)
        """
        # Placeholder formula: modifier decreases as distance increases
        # optimal_range = self.range * 0.5
        # if distance <= optimal_range:
        #     modifier = 1.0
        # elif distance <= self.range:
        #     modifier = 1.0 - ((distance - optimal_range) / optimal_range) * 0.5
        # else:
        #     modifier = 0.5  # Beyond range, significant penalty
        
        # For now, return 1.0 (no modifier)
        return 1.0
    
    def calculate_turn_weapon_effects(
        self, character: Any, target: Any, distance: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate weapon effects with range modifiers.
        
        Args:
            character: Character using the weapon
            target: Target character
            distance: Optional distance to target (if None, uses default)
            
        Returns:
            Dictionary with weapon effects
        """
        # Get base effects
        effects = super().calculate_turn_weapon_effects(character, target)
        
        # Apply range modifier if distance provided
        if distance is not None:
            modifier = self.calculate_range_modifier(distance)
            # Apply modifier to damage (placeholder)
            # effects["total_damage"] *= modifier
            # for effect in effects["effects"]:
            #     if "amount" in effect:
            #         effect["amount"] *= modifier
        
        return effects


class Throwable(Weapon):
    """
    Throwable ranged weapon (throwing knives, axes, etc.).
    
    Attributes:
        range: Maximum effective range
        return_chance: Chance weapon returns after throw
    """
    
    def __init__(
        self,
        name: str,
        short_desc: str,
        long_desc: str,
        weight: float,
        size: float,
        material: str,
        damage_nodes: list[DamageNode],
        range: float,
        return_chance: float = 0.0,
        restrictions: Dict[str, Any] = None,
    ):
        """
        Initialize a throwable weapon.
        
        Args:
            name: Weapon name
            short_desc: Short description
            long_desc: Long description
            weight: Weight of the weapon
            size: Size of the weapon
            material: Material the weapon is made from
            damage_nodes: List of DamageNode instances
            range: Maximum effective range
            return_chance: Chance weapon returns after throw (0.0 to 1.0)
            restrictions: Optional dictionary of restrictions
        """
        super().__init__(
            name=name,
            short_desc=short_desc,
            long_desc=long_desc,
            weight=weight,
            size=size,
            material=material,
            damage_nodes=damage_nodes,
            restrictions=restrictions,
        )
        self.range = range
        self.return_chance = return_chance
        self.weapon_subtype = RANGED_THROWABLE
    
    def calculate_range_modifier(self, distance: float) -> float:
        """
        Calculate damage/accuracy modifier based on distance.
        
        Args:
            distance: Distance to target
            
        Returns:
            Modifier value (1.0 = no change, <1.0 = reduced, >1.0 = increased)
        """
        # Placeholder formula: modifier decreases as distance increases
        # optimal_range = self.range * 0.6
        # if distance <= optimal_range:
        #     modifier = 1.0
        # elif distance <= self.range:
        #     modifier = 1.0 - ((distance - optimal_range) / optimal_range) * 0.6
        # else:
        #     modifier = 0.4  # Beyond range, significant penalty
        
        # For now, return 1.0 (no modifier)
        return 1.0
    
    def calculate_turn_weapon_effects(
        self, character: Any, target: Any, distance: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate weapon effects with range modifiers.
        
        Args:
            character: Character using the weapon
            target: Target character
            distance: Optional distance to target (if None, uses default)
            
        Returns:
            Dictionary with weapon effects, including return status
        """
        import random
        
        # Get base effects
        effects = super().calculate_turn_weapon_effects(character, target)
        
        # Check if weapon returns (placeholder)
        # if random.random() < self.return_chance:
        #     effects["weapon_returned"] = True
        
        # Apply range modifier if distance provided
        if distance is not None:
            modifier = self.calculate_range_modifier(distance)
            # Apply modifier to damage (placeholder)
            # effects["total_damage"] *= modifier
        
        return effects

