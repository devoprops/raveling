"""Weapon base class for all weapons."""

from typing import List, Dict, Any, Optional
from src.models.items.base import Item
from src.models.items.functional_node import FunctionalNode
from src.utils.constants import ITEM_TYPE_WEAPON, FUNCTIONAL_NODE_CLASS_INNATE, FUNCTIONAL_NODE_CLASS_PRIMARY


class Weapon(Item):
    """
    Base class for all weapons.
    
    Attributes:
        functional_nodes: List of FunctionalNode instances that define weapon effects
        slots: Dictionary mapping slot names to FunctionalNode instances (inactive nodes)
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
        restrictions: Dict[str, Any] = None,
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
            functional_nodes: List of FunctionalNode instances
            slots: Optional dictionary of slot_name -> FunctionalNode (inactive nodes)
            restrictions: Optional dictionary of restrictions
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
        )
        self.functional_nodes = functional_nodes or []
        self.slots = slots or {}
    
    def get_active_nodes(self, context: Optional[Dict[str, Any]] = None) -> List[FunctionalNode]:
        """
        Get all active functional nodes (including activated slots).
        
        Args:
            context: Optional context for determining node activity
            
        Returns:
            List of active functional nodes
        """
        active_nodes = []
        
        # Add nodes that are active
        for node in self.functional_nodes:
            if node.is_active(context):
                active_nodes.append(node)
        
        # Add activated slots
        if context and "activated_slots" in context:
            for slot_name in context["activated_slots"]:
                if slot_name in self.slots:
                    active_nodes.append(self.slots[slot_name])
        
        return active_nodes
    
    def fill_slot(self, slot_name: str, node: FunctionalNode) -> bool:
        """
        Fill a slot with a functional node.
        
        Args:
            slot_name: Name of the slot to fill
            node: FunctionalNode to place in the slot
            
        Returns:
            True if slot was filled, False if slot doesn't exist or is already filled
        """
        if slot_name not in self.slots:
            return False
        
        if self.slots[slot_name] is not None:
            return False  # Slot already filled
        
        self.slots[slot_name] = node
        return True
    
    def clear_slot(self, slot_name: str) -> bool:
        """
        Clear a slot (remove the functional node).
        
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
        Calculate all weapon effects for a turn based on functional nodes.
        
        Each functional node is evaluated independently based on its execution probability
        and activity status. Effects can include damage, buffs, debuffs, etc.
        
        Args:
            character: Character using the weapon
            target: Target character or object
            context: Optional context for node activity (e.g., activated_slots)
            
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
        
        # Get active nodes
        active_nodes = self.get_active_nodes(context)
        
        for node in active_nodes:
            # Check if node executes based on probability
            if random.random() < node.execution_probability:
                effect_result = node.execute(character, target)
                effects.append(effect_result)
                
                # Categorize effects
                node_type = effect_result.get("node_type", "unknown")
                
                if node_type == "damage":
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
                
                elif node_type == "buff":
                    buffs.append(effect_result)
                
                elif node_type == "debuff":
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
    
    def get_damage_breakdown(self, character: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get expected damage breakdown for this weapon with a given character.
        
        This provides theoretical/expected values, not actual roll results.
        
        Args:
            character: Character using the weapon
            context: Optional context for node activity
            
        Returns:
            Dictionary with expected damage information:
            - nodes: List of node information
            - expected_damage_per_node: Expected damage contribution per node
            - total_expected_damage: Sum of expected damage
        """
        node_info = []
        total_expected = 0.0
        
        active_nodes = self.get_active_nodes(context)
        
        for node in active_nodes:
            node_data = {
                "node_type": node.node_type,
                "node_class": node.node_class,
                "execution_probability": node.execution_probability,
            }
            
            # Add node-specific information
            if hasattr(node, "element_type"):
                node_data["element"] = node.element_type
            if hasattr(node, "base_damage"):
                # Expected damage = base_damage * execution_probability
                # (simplified - actual calculation would need distribution analysis)
                expected = node.base_damage * node.execution_probability
                node_data["expected_damage"] = expected
                total_expected += expected
            
            node_info.append(node_data)
        
        return {
            "nodes": node_info,
            "total_expected_damage": total_expected,
        }
