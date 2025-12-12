"""Weapon base class for all weapons."""

from typing import List, Dict, Any
from src.models.items.base import Item
from src.models.items.damage_node import DamageNode
from src.utils.constants import ITEM_TYPE_WEAPON


class Weapon(Item):
    """
    Base class for all weapons.
    
    Attributes:
        damage_nodes: List of DamageNode instances that define weapon effects
    """
    
    def __init__(
        self,
        name: str,
        short_desc: str,
        long_desc: str,
        weight: float,
        size: float,
        material: str,
        damage_nodes: List[DamageNode],
        restrictions: Dict[str, Any] = None,
    ):
        """
        Initialize a weapon.
        
        Args:
            name: Weapon name
            short_desc: Short description
            long_desc: Long description
            weight: Weight of the weapon
            size: Size of the weapon
            material: Material the weapon is made from
            damage_nodes: List of DamageNode instances
            restrictions: Optional dictionary of restrictions
        """
        super().__init__(
            name=name,
            short_desc=short_desc,
            long_desc=long_desc,
            item_type=ITEM_TYPE_WEAPON,
            weight=weight,
            size=size,
            material=material,
            restrictions=restrictions,
        )
        self.damage_nodes = damage_nodes or []
    
    def calculate_turn_weapon_effects(
        self, character: Any, target: Any
    ) -> Dict[str, Any]:
        """
        Calculate all weapon effects for a turn based on damage nodes.
        
        Each damage node is evaluated independently based on its execution probability.
        
        Args:
            character: Character using the weapon
            target: Target character or object
            
        Returns:
            Dictionary containing all effects that occurred, including:
            - total_damage: Sum of all damage
            - effects: List of individual effect dictionaries
            - damage_breakdown: Breakdown by damage type
        """
        import random
        
        effects = []
        total_damage = 0.0
        damage_breakdown = {}
        
        for node in self.damage_nodes:
            # Check if node executes based on probability
            if random.random() < node.execution_probability:
                effect_result = node.execute(character, target)
                effects.append(effect_result)
                
                # Accumulate damage
                if "amount" in effect_result:
                    damage_amount = effect_result["amount"]
                    total_damage += damage_amount
                    
                    # Track damage by type
                    damage_type = effect_result.get("damage_type", "unknown")
                    if damage_type not in damage_breakdown:
                        damage_breakdown[damage_type] = 0.0
                    damage_breakdown[damage_type] += damage_amount
        
        return {
            "total_damage": total_damage,
            "effects": effects,
            "damage_breakdown": damage_breakdown,
        }
    
    def calculate_turn_weapon_damage(
        self, character: Any, target: Any
    ) -> float:
        """
        Calculate total weapon damage for a turn.
        
        Args:
            character: Character using the weapon
            target: Target character or object
            
        Returns:
            Total damage amount
        """
        effects = self.calculate_turn_weapon_effects(character, target)
        return effects["total_damage"]
    
    def get_damage_breakdown(self, character: Any) -> Dict[str, Any]:
        """
        Get expected damage breakdown for this weapon with a given character.
        
        This provides theoretical/expected values, not actual roll results.
        
        Args:
            character: Character using the weapon
            
        Returns:
            Dictionary with expected damage information:
            - nodes: List of node information
            - expected_damage_per_node: Expected damage contribution per node
            - total_expected_damage: Sum of expected damage
        """
        node_info = []
        total_expected = 0.0
        
        for node in self.damage_nodes:
            node_data = {
                "node_type": node.node_type,
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

