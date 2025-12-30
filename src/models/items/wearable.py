"""Wearable equipment class."""

from typing import Dict, Any, Optional, List
from src.models.items.base import Item
from src.models.items.functional_node import FunctionalNode
from src.utils.constants import ITEM_TYPE_WEARABLE, EQUIPMENT_SLOTS


class Wearable(Item):
    """
    Wearable equipment that can be equipped to affect defense, stats, or skills.
    
    Attributes:
        defense_bonus: Bonus to defense value
        stat_boosts: Dictionary mapping stat names to boost values
        skill_boosts: Dictionary mapping skill names to boost values
        slot: Equipment slot this item occupies
        functional_nodes: List of FunctionalNode instances for active effects
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
        slot: str,
        defense_bonus: float = 0.0,
        stat_boosts: Optional[Dict[str, float]] = None,
        skill_boosts: Optional[Dict[str, float]] = None,
        functional_nodes: Optional[List[FunctionalNode]] = None,
        slots: Optional[Dict[str, FunctionalNode]] = None,
        restrictions: Optional[Dict[str, Any]] = None,
        affinities: Optional[Dict[str, Dict[str, float]]] = None,
        detriments: Optional[Dict[str, Dict[str, float]]] = None,
        thumbnail_path: Optional[str] = None,
    ):
        """
        Initialize a wearable item.
        
        Args:
            name: Item name
            short_desc: Short description
            long_desc: Long description
            weight_kg: Weight of the item in kilograms
            length_cm: Length of the item in centimeters
            width_cm: Width of the item in centimeters
            material: Material the item is made from
            slot: Equipment slot (must be in EQUIPMENT_SLOTS)
            defense_bonus: Bonus to defense
            stat_boosts: Dictionary of stat name -> boost value
            skill_boosts: Dictionary of skill name -> boost value
        functional_nodes: Optional list of FunctionalNode instances
        slots: Optional dictionary of slot_name -> FunctionalNode (inactive nodes)
        restrictions: Optional dictionary of restrictions
        affinities: Optional dictionary with 'elemental' and 'race' sub-dictionaries.
                   Defaults to 1.0 for all.
        detriments: Optional dictionary with 'elemental' and 'race' sub-dictionaries.
                   Defaults to 1.0 for all.
        thumbnail_path: Optional path to thumbnail/icon image
        """
        super().__init__(
            name=name,
            short_desc=short_desc,
            long_desc=long_desc,
            item_type=ITEM_TYPE_WEARABLE,
            weight_kg=weight_kg,
            length_cm=length_cm,
            width_cm=width_cm,
            material=material,
            restrictions=restrictions,
            affinities=affinities,
            detriments=detriments,
            thumbnail_path=thumbnail_path,
        )
        
        if slot not in EQUIPMENT_SLOTS:
            raise ValueError(f"Invalid slot: {slot}. Must be one of {EQUIPMENT_SLOTS}")
        self.slot = slot
        
        self.defense_bonus = defense_bonus
        self.stat_boosts = stat_boosts or {}
        self.skill_boosts = skill_boosts or {}
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
                if slot_name in self.slots and self.slots[slot_name] is not None:
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
    
    def get_defense_bonus(self) -> float:
        """
        Get the defense bonus provided by this item.
        
        Returns:
            Defense bonus value
        """
        return self.defense_bonus
    
    def get_stat_boosts(self) -> Dict[str, float]:
        """
        Get all stat boosts provided by this item.
        
        Returns:
            Dictionary mapping stat names to boost values
        """
        return self.stat_boosts.copy()
    
    def get_skill_boosts(self) -> Dict[str, float]:
        """
        Get all skill boosts provided by this item.
        
        Returns:
            Dictionary mapping skill names to boost values
        """
        return self.skill_boosts.copy()
    
    def get_stat_boost(self, stat_name: str) -> float:
        """
        Get boost for a specific stat.
        
        Args:
            stat_name: Name of the stat
            
        Returns:
            Boost value (0.0 if stat not boosted)
        """
        return self.stat_boosts.get(stat_name, 0.0)
    
    def get_skill_boost(self, skill_name: str) -> float:
        """
        Get boost for a specific skill.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Boost value (0.0 if skill not boosted)
        """
        return self.skill_boosts.get(skill_name, 0.0)
    
    def calculate_equipment_effects(
        self, character: Any, target: Optional[Any] = None, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate all effects from functional nodes when equipment is active.
        
        Args:
            character: Character wearing the equipment
            target: Optional target character
            context: Optional context for node activity
            
        Returns:
            Dictionary containing all effects
        """
        import random
        
        effects = []
        buffs = []
        debuffs = []
        
        # Get active nodes
        active_nodes = self.get_active_nodes(context)
        
        for node in active_nodes:
            # Check if node executes based on probability
            if random.random() < node.execution_probability:
                effect_result = node.execute(character, target or character)
                effects.append(effect_result)
                
                # Categorize effects
                node_type = effect_result.get("node_type", "unknown")
                
                if node_type == "buff":
                    buffs.append(effect_result)
                elif node_type == "debuff":
                    debuffs.append(effect_result)
        
        return {
            "effects": effects,
            "buffs": buffs,
            "debuffs": debuffs,
        }
