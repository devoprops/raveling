"""Melee weapon subclasses."""

from typing import Dict, Any, Optional, List
from src.models.items.weapon import Weapon
from src.models.items.functional_node import FunctionalNode
from src.utils.constants import MELEE_BLADED, MELEE_BLUNT, MELEE_FLAILED


class BladedWeapon(Weapon):
    """
    Bladed melee weapon (swords, daggers, etc.).
    
    Attributes:
        blade_length: Length of the blade
        sharpness: Sharpness rating (affects damage)
    """
    
    def __init__(
        self,
        name: str,
        short_desc: str,
        long_desc: str,
        weight_kg: float,
        length_cm: float,
        width_cm: float,
        material: str,
        functional_nodes: List[FunctionalNode],
        slots: Optional[Dict[str, FunctionalNode]] = None,
        blade_length: float,
        sharpness: float,
        restrictions: Dict[str, Any] = None,
    ):
        """
        Initialize a bladed weapon.
        
        Args:
            name: Weapon name
            short_desc: Short description
            long_desc: Long description
            weight_kg: Weight of the weapon in kilograms
            length_cm: Length of the weapon in centimeters
            width_cm: Width of the weapon in centimeters
            material: Material the weapon is made from
            functional_nodes: List of FunctionalNode instances
            slots: Optional dictionary of slot_name -> FunctionalNode
            blade_length: Length of the blade
            sharpness: Sharpness rating
            restrictions: Optional dictionary of restrictions
        """
        super().__init__(
            name=name,
            short_desc=short_desc,
            long_desc=long_desc,
            weight_kg=weight_kg,
            length_cm=length_cm,
            width_cm=width_cm,
            material=material,
            functional_nodes=functional_nodes,
            slots=slots,
            restrictions=restrictions,
        )
        self.blade_length = blade_length
        self.sharpness = sharpness
        self.weapon_subtype = MELEE_BLADED
    
    def calculate_turn_weapon_effects(
        self, character: Any, target: Any
    ) -> Dict[str, Any]:
        """
        Calculate weapon effects with bladed weapon modifiers.
        
        Args:
            character: Character using the weapon
            target: Target character
            
        Returns:
            Dictionary with weapon effects
        """
        # Get base effects
        effects = super().calculate_turn_weapon_effects(character, target)
        
        # Apply bladed weapon modifiers (placeholder)
        # Sharpness could modify damage: damage *= (1 + sharpness / 100)
        # Blade length could affect reach/hit probability
        
        return effects


class BluntWeapon(Weapon):
    """
    Blunt melee weapon (maces, hammers, clubs, etc.).
    
    Attributes:
        impact_force: Impact force rating (affects damage)
        stun_chance: Chance to stun on hit
    """
    
    def __init__(
        self,
        name: str,
        short_desc: str,
        long_desc: str,
        weight_kg: float,
        length_cm: float,
        width_cm: float,
        material: str,
        functional_nodes: List[FunctionalNode],
        slots: Optional[Dict[str, FunctionalNode]] = None,
        impact_force: float,
        stun_chance: float = 0.0,
        restrictions: Dict[str, Any] = None,
    ):
        """
        Initialize a blunt weapon.
        
        Args:
            name: Weapon name
            short_desc: Short description
            long_desc: Long description
            weight_kg: Weight of the weapon in kilograms
            length_cm: Length of the weapon in centimeters
            width_cm: Width of the weapon in centimeters
            material: Material the weapon is made from
            functional_nodes: List of FunctionalNode instances
            slots: Optional dictionary of slot_name -> FunctionalNode
            impact_force: Impact force rating
            stun_chance: Chance to stun target (0.0 to 1.0)
            restrictions: Optional dictionary of restrictions
        """
        super().__init__(
            name=name,
            short_desc=short_desc,
            long_desc=long_desc,
            weight_kg=weight_kg,
            length_cm=length_cm,
            width_cm=width_cm,
            material=material,
            functional_nodes=functional_nodes,
            slots=slots,
            restrictions=restrictions,
        )
        self.impact_force = impact_force
        self.stun_chance = stun_chance
        self.weapon_subtype = MELEE_BLUNT
    
    def calculate_turn_weapon_effects(
        self, character: Any, target: Any
    ) -> Dict[str, Any]:
        """
        Calculate weapon effects with blunt weapon modifiers.
        
        Args:
            character: Character using the weapon
            target: Target character
            
        Returns:
            Dictionary with weapon effects, including potential stun
        """
        import random
        
        # Get base effects
        effects = super().calculate_turn_weapon_effects(character, target)
        
        # Check for stun effect (placeholder)
        # if random.random() < self.stun_chance:
        #     effects["stun"] = True
        #     effects["stun_duration"] = calculate_stun_duration(character, self.impact_force)
        
        # Apply impact force modifiers (placeholder)
        # damage *= (1 + impact_force / 100)
        
        return effects


class FlailedWeapon(Weapon):
    """
    Flailed melee weapon (flails, whips, etc.).
    
    Attributes:
        chain_length: Length of chain/flail
        wrap_chance: Chance to wrap around target
    """
    
    def __init__(
        self,
        name: str,
        short_desc: str,
        long_desc: str,
        weight_kg: float,
        length_cm: float,
        width_cm: float,
        material: str,
        functional_nodes: List[FunctionalNode],
        slots: Optional[Dict[str, FunctionalNode]] = None,
        chain_length: float,
        wrap_chance: float = 0.0,
        restrictions: Dict[str, Any] = None,
    ):
        """
        Initialize a flailed weapon.
        
        Args:
            name: Weapon name
            short_desc: Short description
            long_desc: Long description
            weight_kg: Weight of the weapon in kilograms
            length_cm: Length of the weapon in centimeters
            width_cm: Width of the weapon in centimeters
            material: Material the weapon is made from
            functional_nodes: List of FunctionalNode instances
            slots: Optional dictionary of slot_name -> FunctionalNode
            chain_length: Length of chain/flail
            wrap_chance: Chance to wrap around target (0.0 to 1.0)
            restrictions: Optional dictionary of restrictions
        """
        super().__init__(
            name=name,
            short_desc=short_desc,
            long_desc=long_desc,
            weight_kg=weight_kg,
            length_cm=length_cm,
            width_cm=width_cm,
            material=material,
            functional_nodes=functional_nodes,
            slots=slots,
            restrictions=restrictions,
        )
        self.chain_length = chain_length
        self.wrap_chance = wrap_chance
        self.weapon_subtype = MELEE_FLAILED
    
    def calculate_turn_weapon_effects(
        self, character: Any, target: Any
    ) -> Dict[str, Any]:
        """
        Calculate weapon effects with flailed weapon modifiers.
        
        Args:
            character: Character using the weapon
            target: Target character
            
        Returns:
            Dictionary with weapon effects, including potential wrap
        """
        import random
        
        # Get base effects
        effects = super().calculate_turn_weapon_effects(character, target)
        
        # Check for wrap effect (placeholder)
        # if random.random() < self.wrap_chance:
        #     effects["wrapped"] = True
        #     effects["wrap_duration"] = calculate_wrap_duration(character, self.chain_length)
        
        return effects

