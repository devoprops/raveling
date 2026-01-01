"""Weapon damage analysis utilities for simulating weapon effects."""

import random
from typing import Dict, Any, List, Optional, Tuple
from src.utils.common.distributions import (
    create_distribution_function,
    sample_uniform,
    sample_gaussian,
    sample_skewnorm,
    sample_bimodal,
    sample_die_roll,
)


def simulate_damage(weapon_config: Dict[str, Any], num_strikes: int) -> Dict[str, Any]:
    """
    Simulate weapon damage over N strikes.
    
    Supports both old effector-based configs and new EffectStyle-based configs.
    For EffectStyles:
    - Primary styles: Mutually exclusive, select one per strike (by subtype or relative weights)
    - Secondary styles: Independent, execute based on execution_probability
    
    Args:
        weapon_config: Weapon configuration dictionary containing effectors or effect_styles
        num_strikes: Number of strikes to simulate
        
    Returns:
        Dictionary containing:
        - strikes: List of strike numbers [1, 2, ..., N]
        - cumulative_damage: List of cumulative damage after each strike
        - damage_values: List of all individual damage values from all strikes
        - damage_per_strike: List of total damage per strike
        - effector_breakdown: Dict mapping effector_id to per-strike damage lists
        - effector_cumulative: Dict mapping effector_id to cumulative damage lists
        - style_breakdown: Dict mapping style_id to per-strike damage lists (if using styles)
        - style_cumulative: Dict mapping style_id to cumulative damage lists (if using styles)
        - min_damage: Minimum damage value observed
        - max_damage: Maximum damage value observed
    """
    # Check if using EffectStyles or legacy effectors
    primary_styles = weapon_config.get("primary_effect_styles", [])
    secondary_styles = weapon_config.get("secondary_effect_styles", [])
    effectors = weapon_config.get("effectors", [])
    
    use_styles = len(primary_styles) > 0 or len(secondary_styles) > 0
    
    strikes = []
    cumulative_damage = []
    damage_values = []
    damage_per_strike = []
    cumulative_total = 0.0
    
    # Track per-effector data (for legacy support)
    effector_breakdown: Dict[str, List[float]] = {}
    effector_cumulative: Dict[str, List[float]] = {}
    effector_cumulative_totals: Dict[str, float] = {}
    
    # Track per-style data (for EffectStyles)
    style_breakdown: Dict[str, List[float]] = {}
    style_cumulative: Dict[str, List[float]] = {}
    style_cumulative_totals: Dict[str, float] = {}
    
    if use_styles:
        # Initialize style tracking
        for style in primary_styles + secondary_styles:
            style_id = style.get("name", "") or style.get("subtype", "")
            style_breakdown[style_id] = []
            style_cumulative[style_id] = []
            style_cumulative_totals[style_id] = 0.0
    else:
        # Initialize effector tracking (legacy)
        for idx, effector in enumerate(effectors):
            effector_id = f"{effector.get('effector_name', f'effector_{idx}')}"
            effector_breakdown[effector_id] = []
            effector_cumulative[effector_id] = []
            effector_cumulative_totals[effector_id] = 0.0
    
    for strike_num in range(1, num_strikes + 1):
        strike_damage = 0.0
        
        if use_styles:
            # Process primary styles (mutually exclusive - select one)
            if primary_styles:
                selected_primary = _select_primary_style(primary_styles, subtype=None)
                selected_style_id = None
                
                if selected_primary:
                    primary_damage, individual_damages = _execute_style_damage_with_breakdown(selected_primary)
                    strike_damage += primary_damage
                    # Add individual damage values from all effectors
                    damage_values.extend(individual_damages)
                    
                    selected_style_id = selected_primary.get("name", "") or selected_primary.get("subtype", "")
                
                # Update tracking for all primary styles
                for style in primary_styles:
                    style_id = style.get("name", "") or style.get("subtype", "")
                    if style_id == selected_style_id and selected_primary:
                        style_damage = primary_damage
                    else:
                        style_damage = 0.0
                    
                    style_breakdown[style_id].append(style_damage)
                    style_cumulative_totals[style_id] += style_damage
                    style_cumulative[style_id].append(style_cumulative_totals[style_id])
            
            # Process secondary styles (independent - can all execute)
            for style in secondary_styles:
                style_id = style.get("name", "") or style.get("subtype", "")
                style_damage_this_strike = 0.0
                
                execution_prob = style.get("execution_probability", 1.0)
                if random.random() < execution_prob:
                    style_damage_this_strike, individual_damages = _execute_style_damage_with_breakdown(style)
                    strike_damage += style_damage_this_strike
                    # Add individual damage values from all effectors
                    damage_values.extend(individual_damages)
                
                style_breakdown[style_id].append(style_damage_this_strike)
                style_cumulative_totals[style_id] += style_damage_this_strike
                style_cumulative[style_id].append(style_cumulative_totals[style_id])
        else:
            # Legacy effector-based processing
            for idx, effector in enumerate(effectors):
                effector_id = f"{effector.get('effector_name', f'effector_{idx}')}"
                effector_damage_this_strike = 0.0
                
                # Check execution probability
                execution_prob = effector.get("execution_probability", 1.0)
                if random.random() < execution_prob:
                    # Get effector type
                    effector_type = effector.get("effector_type", "")
                    
                    # Only process damage effectors for now
                    if effector_type == "damage":
                        # Get distribution parameters
                        dist_params = effector.get("distribution_parameters", {})
                        if dist_params:
                            dist_type = dist_params.get("type", "uniform")
                            params = dist_params.get("params", {})
                            
                            # Sample damage from distribution
                            try:
                                damage = _sample_damage(dist_type, params)
                                damage = max(0.0, damage)  # Ensure non-negative
                                strike_damage += damage
                                effector_damage_this_strike = damage
                                damage_values.append(damage)
                            except Exception as e:
                                print(f"Warning: Failed to sample damage for effector: {e}")
                
                # Update effector tracking
                effector_breakdown[effector_id].append(effector_damage_this_strike)
                effector_cumulative_totals[effector_id] += effector_damage_this_strike
                effector_cumulative[effector_id].append(effector_cumulative_totals[effector_id])
        
        # Update cumulative damage
        cumulative_total += strike_damage
        strikes.append(strike_num)
        cumulative_damage.append(cumulative_total)
        damage_per_strike.append(strike_damage)
    
    # Calculate min/max
    min_damage = min(damage_values) if damage_values else 0.0
    max_damage = max(damage_values) if damage_values else 0.0
    
    result = {
        "strikes": strikes,
        "cumulative_damage": cumulative_damage,
        "damage_values": damage_values,
        "damage_per_strike": damage_per_strike,
        "min_damage": min_damage,
        "max_damage": max_damage,
    }
    
    if use_styles:
        result["style_breakdown"] = style_breakdown
        result["style_cumulative"] = style_cumulative
    else:
        result["effector_breakdown"] = effector_breakdown
        result["effector_cumulative"] = effector_cumulative
    
    return result


def _select_primary_style(primary_styles: List[Dict[str, Any]], subtype: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Select a primary effect style based on subtype or relative weights.
    
    Args:
        primary_styles: List of primary style configs
        subtype: Optional subtype to select
        
    Returns:
        Selected style config, or None
    """
    if not primary_styles:
        return None
    
    if subtype:
        # Find style with matching subtype
        for style in primary_styles:
            if style.get("subtype") == subtype:
                return style
        return None
    
    # Use relative weights
    total_weight = sum(style.get("execution_probability", 1.0) for style in primary_styles)
    if total_weight == 0:
        return None
    
    rand = random.random() * total_weight
    cumulative = 0.0
    for style in primary_styles:
        cumulative += style.get("execution_probability", 1.0)
        if rand <= cumulative:
            return style
    
    # Fallback to first style
    return primary_styles[0]


def _execute_style_damage(style: Dict[str, Any]) -> float:
    """
    Execute a style's effectors and return total damage amount.
    
    Supports both single effector (backwards compat) and multiple effectors (new format).
    Processes all damage effectors and sums their damage.
    
    Args:
        style: Style configuration dictionary
        
    Returns:
        Total damage amount (0.0 if no damage effectors or execution fails)
    """
    total_damage, _ = _execute_style_damage_with_breakdown(style)
    return total_damage


def _execute_style_damage_with_breakdown(style: Dict[str, Any]) -> Tuple[float, List[float]]:
    """
    Execute a style's effectors and return total damage amount and individual damages.
    
    Supports both single effector (backwards compat) and multiple effectors (new format).
    Processes all damage effectors and sums their damage.
    
    Args:
        style: Style configuration dictionary
        
    Returns:
        Tuple of (total_damage, list_of_individual_damages)
    """
    total_damage = 0.0
    individual_damages = []
    
    # Handle multiple effectors (new format)
    effectors = style.get("effectors", [])
    if effectors and isinstance(effectors, list):
        for effector in effectors:
            damage = _execute_single_effector(effector)
            if damage > 0:
                total_damage += damage
                individual_damages.append(damage)
    else:
        # Handle single effector (backwards compat)
        effector = style.get("effector", {})
        if effector:
            damage = _execute_single_effector(effector)
            if damage > 0:
                total_damage += damage
                individual_damages.append(damage)
    
    return total_damage, individual_damages


def _execute_single_effector(effector: Dict[str, Any]) -> float:
    """
    Execute a single effector and return damage amount.
    
    Args:
        effector: Effector configuration dictionary
        
    Returns:
        Damage amount (0.0 if not damage or execution fails)
    """
    if not effector:
        return 0.0
    
    effector_type = effector.get("effector_type", "")
    
    if effector_type != "damage":
        return 0.0
    
    # Get distribution parameters
    dist_params = effector.get("distribution_parameters", {})
    if not dist_params:
        return 0.0
    
    dist_type = dist_params.get("type", "uniform")
    params = dist_params.get("params", {})
    
    try:
        damage = _sample_damage(dist_type, params)
        return max(0.0, damage)
    except Exception as e:
        print(f"Warning: Failed to sample damage for effector: {e}")
        return 0.0


def _sample_damage(dist_type: str, params: Dict[str, Any]) -> float:
    """
    Sample a damage value from a distribution.
    
    Args:
        dist_type: Type of distribution (uniform, gaussian, skewnorm, bimodal, die_roll)
        params: Distribution parameters
        
    Returns:
        Sampled damage value
    """
    if dist_type == "uniform":
        min_val = params.get("min_val", params.get("min", 0.0))
        max_val = params.get("max_val", params.get("max", 1.0))
        return sample_uniform(min_val, max_val)
    
    elif dist_type == "gaussian":
        mean = params.get("mean", 0.0)
        std_dev = params.get("std_dev", 1.0)
        return sample_gaussian(mean, std_dev)
    
    elif dist_type == "skewnorm":
        mean = params.get("mean", 0.0)
        std_dev = params.get("std_dev", 1.0)
        skew = params.get("skew", 0.0)
        return sample_skewnorm(mean, std_dev, skew)
    
    elif dist_type == "bimodal":
        mean1 = params.get("mean1", 0.0)
        std1 = params.get("std1", 1.0)
        mean2 = params.get("mean2", 0.0)
        std2 = params.get("std2", 1.0)
        weight = params.get("weight", 0.5)
        return sample_bimodal(mean1, std1, mean2, std2, weight)
    
    elif dist_type == "die_roll":
        notation = params.get("notation", "1d6")
        return float(sample_die_roll(notation))
    
    else:
        raise ValueError(f"Unknown distribution type: {dist_type}")

