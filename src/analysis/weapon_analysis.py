"""Weapon analysis utilities for damage calculations and distributions."""

from typing import Dict, Any, List, Optional
import random
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from src.models.items.weapon import Weapon
from src.models.characters.base import Character


def damage_over_cycles(
    weapon: Weapon,
    character: Character,
    target: Character,
    num_cycles: int,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Calculate damage over multiple cycles with breakdown by node.
    
    Args:
        weapon: Weapon to analyze
        character: Character using the weapon
        target: Target character
        num_cycles: Number of cycles to simulate
        context: Optional context for node activity
        
    Returns:
        Dictionary containing:
        - cycles: List of cycle results
        - total_damage: Total damage across all cycles
        - average_damage: Average damage per cycle
        - node_breakdown: Breakdown of damage by node
    """
    cycles = []
    total_damage = 0.0
    node_breakdown = {}
    
    for cycle in range(num_cycles):
        # Set random seed for reproducibility if needed
        # random.seed(cycle)
        
        effects = weapon.calculate_turn_weapon_effects(character, target, context)
        cycle_damage = effects["total_damage"]
        
        cycles.append({
            "cycle": cycle + 1,
            "total_damage": cycle_damage,
            "effects": effects["effects"],
            "damage_breakdown": effects["damage_breakdown"],
        })
        
        total_damage += cycle_damage
        
        # Track node contributions
        for effect in effects["effects"]:
            if "amount" in effect:
                node_key = f"{effect.get('node_type', 'unknown')}_{effect.get('node_class', 'unknown')}"
                if node_key not in node_breakdown:
                    node_breakdown[node_key] = 0.0
                node_breakdown[node_key] += effect["amount"]
    
    average_damage = total_damage / num_cycles if num_cycles > 0 else 0.0
    
    return {
        "cycles": cycles,
        "total_damage": total_damage,
        "average_damage": average_damage,
        "node_breakdown": node_breakdown,
        "num_cycles": num_cycles,
    }


def damage_distribution(
    weapon: Weapon,
    character: Character,
    target: Character,
    num_cycles: int,
    context: Optional[Dict[str, Any]] = None,
) -> Figure:
    """
    Create a histogram showing damage distribution over cycles with different colors for nodes.
    
    Args:
        weapon: Weapon to analyze
        character: Character using the weapon
        target: Target character
        num_cycles: Number of cycles to simulate
        context: Optional context for node activity
        
    Returns:
        Matplotlib Figure with histogram
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Get damage data
    analysis_data = damage_over_cycles(weapon, character, target, num_cycles, context)
    
    # Extract damage values by node type
    node_data = {}
    all_damage = []
    
    for cycle in analysis_data["cycles"]:
        for effect in cycle["effects"]:
            if "amount" in effect:
                node_type = effect.get("node_type", "unknown")
                node_class = effect.get("node_class", "unknown")
                node_key = f"{node_type}_{node_class}"
                
                if node_key not in node_data:
                    node_data[node_key] = []
                
                node_data[node_key].append(effect["amount"])
                all_damage.append(effect["amount"])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if node_data:
        # Stack histograms by node type
        bins = np.linspace(0, max(all_damage) if all_damage else 1, 30)
        
        bottom = None
        colors = plt.cm.Set3(np.linspace(0, 1, len(node_data)))
        
        for idx, (node_key, damage_values) in enumerate(node_data.items()):
            counts, bin_edges = np.histogram(damage_values, bins=bins)
            if bottom is None:
                ax.bar(bin_edges[:-1], counts, width=np.diff(bin_edges), 
                      label=node_key, color=colors[idx], alpha=0.7)
                bottom = counts
            else:
                ax.bar(bin_edges[:-1], counts, width=np.diff(bin_edges),
                      bottom=bottom, label=node_key, color=colors[idx], alpha=0.7)
                bottom = bottom + counts
        
        ax.set_xlabel("Damage Amount")
        ax.set_ylabel("Frequency")
        ax.set_title(f"Damage Distribution Over {num_cycles} Cycles")
        ax.legend()
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, "No damage data available", 
               ha="center", va="center", transform=ax.transAxes)
        ax.set_title("Damage Distribution")
    
    plt.tight_layout()
    return fig


def plot_damage_over_cycles(
    weapon: Weapon,
    character: Character,
    target: Character,
    num_cycles: int,
    context: Optional[Dict[str, Any]] = None,
) -> Figure:
    """
    Create a line plot showing damage over cycles with breakdown by node.
    
    Args:
        weapon: Weapon to analyze
        character: Character using the weapon
        target: Target character
        num_cycles: Number of cycles to simulate
        context: Optional context for node activity
        
    Returns:
        Matplotlib Figure with line plot
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Get damage data
    analysis_data = damage_over_cycles(weapon, character, target, num_cycles, context)
    
    # Extract damage by cycle and node
    cycles = list(range(1, num_cycles + 1))
    node_data = {}
    
    for cycle_result in analysis_data["cycles"]:
        cycle_num = cycle_result["cycle"]
        for effect in cycle_result["effects"]:
            if "amount" in effect:
                node_type = effect.get("node_type", "unknown")
                node_class = effect.get("node_class", "unknown")
                node_key = f"{node_type}_{node_class}"
                
                if node_key not in node_data:
                    node_data[node_key] = []
                
                # Pad with zeros if needed
                while len(node_data[node_key]) < cycle_num - 1:
                    node_data[node_key].append(0.0)
                
                node_data[node_key].append(effect["amount"])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(node_data)))
    
    for idx, (node_key, damage_values) in enumerate(node_data.items()):
        # Pad to match cycle count
        while len(damage_values) < num_cycles:
            damage_values.append(0.0)
        
        ax.plot(cycles, damage_values[:num_cycles], 
               label=node_key, color=colors[idx], marker='o', markersize=3, linewidth=1.5)
    
    # Plot total damage
    total_damage_per_cycle = [c["total_damage"] for c in analysis_data["cycles"]]
    ax.plot(cycles, total_damage_per_cycle, 
           label="Total Damage", color="black", linewidth=2, linestyle="--")
    
    ax.set_xlabel("Cycle")
    ax.set_ylabel("Damage")
    ax.set_title(f"Damage Over {num_cycles} Cycles")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

