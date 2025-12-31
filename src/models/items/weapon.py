"""Weapon base class for all weapons."""

import random
from typing import List, Dict, Any, Optional
from src.models.items.base import Item
from src.models.effectors.base import Effector
from src.models.effect_styles.base import EffectStyle
from src.utils.constants import ITEM_TYPE_WEAPON


class Weapon(Item):
    """
    Base class for all weapons.
    
    Attributes:
        effectors: List of Effector instances that define weapon effects
        slots: Dictionary mapping slot names to Effector instances (inactive effectors)
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
        effectors: Optional[List[Effector]] = None,
        primary_effect_styles: Optional[List[EffectStyle]] = None,
        secondary_effect_styles: Optional[List[EffectStyle]] = None,
        slots: Optional[Dict[str, Effector]] = None,
        restrictions: Dict[str, Any] = None,
        affinities: Optional[Dict[str, Dict[str, float]]] = None,
        detriments: Optional[Dict[str, Dict[str, float]]] = None,
        auxiliary_slots: int = 0,
        size_constraints: Optional[tuple] = None,
        thumbnail_path: Optional[str] = None,
    ):
        """
        Initialize a weapon.
        
        Args:
            name: Weapon name
            short_desc: Short description
            long_desc: Long description
            weight_kg: Weight of the weapon in kilograms
            length_cm: Length of the weapon in centimeters
            width_cm: Width of the weapon in centimeters
            material: Material the weapon is made from
            effectors: List of Effector instances (deprecated, use effect_styles instead)
            primary_effect_styles: List of EffectStyle instances (mutually exclusive)
            secondary_effect_styles: List of EffectStyle instances (can execute together)
            slots: Optional dictionary of slot_name -> Effector (inactive effectors)
            restrictions: Optional dictionary of restrictions
            affinities: Optional dictionary with 'elemental' and 'race' sub-dictionaries.
                       Defaults to 1.0 for all.
            detriments: Optional dictionary with 'elemental' and 'race' sub-dictionaries.
                       Defaults to 1.0 for all.
            auxiliary_slots: Number of auxiliary slots the item provides (default: 0)
            size_constraints: Optional tuple/list [min, max] for character size requirements
            thumbnail_path: Optional path to thumbnail/icon image
        """
        super().__init__(
            name=name,
            short_desc=short_desc,
            long_desc=long_desc,
            item_type=ITEM_TYPE_WEAPON,
            weight_kg=weight_kg,
            length_cm=length_cm,
            width_cm=width_cm,
            material=material,
            restrictions=restrictions,
            affinities=affinities,
            detriments=detriments,
            auxiliary_slots=auxiliary_slots,
            size_constraints=size_constraints,
            thumbnail_path=thumbnail_path,
        )
        # Keep effectors for backwards compatibility (deprecated)
        self.effectors = effectors or []
        self.primary_effect_styles = primary_effect_styles or []
        self.secondary_effect_styles = secondary_effect_styles or []
        self.slots = slots or {}
    
    def get_active_effectors(self, context: Optional[Dict[str, Any]] = None) -> List[Effector]:
        """
        Get all active effectors (including activated slots).
        
        Args:
            context: Optional context for determining effector activity
            
        Returns:
            List of active effectors
        """
        active_effectors = []
        
        # Add all effectors (they're always active by default)
        # In the future, we could add activation logic based on context
        active_effectors.extend(self.effectors)
        
        # Add activated slots
        if context and "activated_slots" in context:
            for slot_name in context["activated_slots"]:
                if slot_name in self.slots and self.slots[slot_name] is not None:
                    active_effectors.append(self.slots[slot_name])
        
        return active_effectors
    
    def fill_slot(self, slot_name: str, effector: Effector) -> bool:
        """
        Fill a slot with an effector.
        
        Args:
            slot_name: Name of the slot to fill
            effector: Effector to place in the slot
            
        Returns:
            True if slot was filled, False if slot doesn't exist or is already filled
        """
        if slot_name not in self.slots:
            return False
        
        if self.slots[slot_name] is not None:
            return False  # Slot already filled
        
        self.slots[slot_name] = effector
        return True
    
    def clear_slot(self, slot_name: str) -> bool:
        """
        Clear a slot (remove the effector).
        
        Args:
            slot_name: Name of the slot to clear
            
        Returns:
            True if slot was cleared, False if slot doesn't exist or is empty
        """
        if slot_name not in self.slots:
            return False
        
        if self.slots[slot_name] is None:
            return False  # Slot already empty
        
        self.slots[slot_name] = None
        return True
    
    def calculate_turn_weapon_effects(
        self, character: Any, target: Any, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate all weapon effects for a turn based on effectors.
        
        Each effector is evaluated independently based on its execution probability.
        Effects can include damage, buffs, debuffs, etc.
        
        Args:
            character: Character using the weapon
            target: Target character or object
            context: Optional context for effector activity (e.g., activated_slots)
            
        Returns:
            Dictionary containing all effects that occurred, including:
            - total_damage: Sum of all damage
            - effects: List of individual effect dictionaries
            - damage_breakdown: Breakdown by damage type
            - buffs: List of buff effects
            - debuffs: List of debuff effects
        """
        import random
        
        effects = []
        total_damage = 0.0
        damage_breakdown = {}
        buffs = []
        debuffs = []
        
        # Get active effectors
        active_effectors = self.get_active_effectors(context)
        
        for effector in active_effectors:
            # Check execution probability (default 1.0 if not specified)
            execution_prob = getattr(effector, 'execution_probability', 1.0)
            if random.random() < execution_prob:
                effect_result = effector.execute(character, target)
                effects.append(effect_result)
                
                # Categorize effects
                effector_type = effect_result.get("effector_type", "unknown")
                
                if effector_type == "damage":
                    # Accumulate damage
                    if "amount" in effect_result:
                        damage_amount = effect_result["amount"]
                        total_damage += damage_amount
                        
                        # Track damage by type
                        damage_subtype = effect_result.get("damage_subtype", "unknown")
                        if damage_subtype not in damage_breakdown:
                            damage_breakdown[damage_subtype] = 0.0
                        damage_breakdown[damage_subtype] += damage_amount
                        
                        # Track elemental damage separately
                        if "element" in effect_result:
                            element_key = f"{damage_subtype}_{effect_result['element']}"
                            if element_key not in damage_breakdown:
                                damage_breakdown[element_key] = 0.0
                            damage_breakdown[element_key] += damage_amount
                
                elif effector_type == "buff":
                    buffs.append(effect_result)
                
                elif effector_type == "debuff":
                    debuffs.append(effect_result)
        
        return {
            "total_damage": total_damage,
            "effects": effects,
            "damage_breakdown": damage_breakdown,
            "buffs": buffs,
            "debuffs": debuffs,
        }
    
    def calculate_turn_weapon_damage(
        self, character: Any, target: Any, context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate total weapon damage for a turn.
        
        Args:
            character: Character using the weapon
            target: Target character or object
            context: Optional context for node activity
            
        Returns:
            Total damage amount
        """
        effects = self.calculate_turn_weapon_effects(character, target, context)
        return effects["total_damage"]
    
    def select_primary_style(self, subtype: Optional[str] = None) -> Optional[EffectStyle]:
        """
        Select a primary effect style based on subtype or relative weights.
        
        Primary styles are mutually exclusive. If a subtype is specified, that style
        is selected. Otherwise, selection is based on relative weights of execution_probability.
        
        Args:
            subtype: Optional subtype to select (e.g., "slash", "thrust")
                    If None, uses relative weight selection
        
        Returns:
            Selected EffectStyle, or None if no primary styles exist
        """
        if not self.primary_effect_styles:
            return None
        
        if subtype:
            # Find style with matching subtype
            for style in self.primary_effect_styles:
                if style.subtype == subtype:
                    return style
            return None
        
        # Use relative weights
        total_weight = sum(style.execution_probability for style in self.primary_effect_styles)
        if total_weight == 0:
            return None
        
        rand = random.random() * total_weight
        cumulative = 0.0
        for style in self.primary_effect_styles:
            cumulative += style.execution_probability
            if rand <= cumulative:
                return style
        
        # Fallback to first style (shouldn't happen)
        return self.primary_effect_styles[0]
    
    def calculate_primary_damage(
        self, character: Any, target: Any, subtype: Optional[str] = None
    ) -> float:
        """
        Calculate damage from primary effect styles.
        
        Primary styles are mutually exclusive. If subtype is specified, uses that style.
        Otherwise, selects a style based on relative weights.
        
        Args:
            character: Character using the weapon
            target: Target character
            subtype: Optional subtype to use (e.g., "slash", "thrust")
        
        Returns:
            Damage amount (0.0 if no primary styles or style doesn't execute)
        """
        selected_style = self.select_primary_style(subtype)
        if not selected_style:
            return 0.0
        
        # Check execution probability
        if random.random() >= selected_style.execution_probability:
            return 0.0
        
        # Execute the style's effector
        result = selected_style.execute(character, target)
        return result.get("amount", 0.0)
    
    def get_damage_breakdown(self, character: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get expected damage breakdown for this weapon with a given character.
        
        This provides theoretical/expected values, not actual roll results.
        
        Args:
            character: Character using the weapon
            context: Optional context for effector activity
            
        Returns:
            Dictionary with expected damage information:
            - effectors: List of effector information
            - expected_damage_per_effector: Expected damage contribution per effector
            - total_expected_damage: Sum of expected damage
        """
        effector_info = []
        total_expected = 0.0
        
        active_effectors = self.get_active_effectors(context)
        
        for effector in active_effectors:
            effector_data = {
                "effector_type": effector.effector_type,
                "effector_name": effector.effector_name,
                "execution_probability": getattr(effector, 'execution_probability', 1.0),
            }
            
            # Add effector-specific information
            if hasattr(effector, "element_type"):
                effector_data["element"] = effector.element_type
            if hasattr(effector, "base_damage"):
                # Expected damage = base_damage * execution_probability
                # (simplified - actual calculation would need distribution analysis)
                expected = effector.base_damage * effector_data["execution_probability"]
                effector_data["expected_damage"] = expected
                total_expected += expected
            
            effector_info.append(effector_data)
        
        return {
            "effectors": effector_info,
            "total_expected_damage": total_expected,
        }
