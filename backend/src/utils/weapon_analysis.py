"""Weapon damage analysis utilities for simulating weapon effects."""

import random
from typing import Dict, Any, List
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
    
    For each strike:
    - Get active effectors from weapon config
    - For each effector:
      - Check execution probability (random roll)
      - If executes, sample from distribution parameters
      - Accumulate damage
    
    Args:
        weapon_config: Weapon configuration dictionary containing effectors
        num_strikes: Number of strikes to simulate
        
    Returns:
        Dictionary containing:
        - strikes: List of strike numbers [1, 2, ..., N]
        - cumulative_damage: List of cumulative damage after each strike
        - damage_values: List of all individual damage values from all strikes
        - min_damage: Minimum damage value observed
        - max_damage: Maximum damage value observed
    """
    effectors = weapon_config.get("effectors", [])
    
    strikes = []
    cumulative_damage = []
    damage_values = []
    cumulative_total = 0.0
    
    for strike_num in range(1, num_strikes + 1):
        strike_damage = 0.0
        
        # Process each effector
        for effector in effectors:
            # Check execution probability
            execution_prob = effector.get("execution_probability", 1.0)
            if random.random() >= execution_prob:
                continue  # Effector doesn't execute this strike
            
            # Get effector type
            effector_type = effector.get("effector_type", "")
            
            # Only process damage effectors for now
            if effector_type == "damage":
                # Get distribution parameters
                dist_params = effector.get("distribution_parameters", {})
                if not dist_params:
                    continue
                
                dist_type = dist_params.get("type", "uniform")
                params = dist_params.get("params", {})
                
                # Sample damage from distribution
                try:
                    damage = _sample_damage(dist_type, params)
                    damage = max(0.0, damage)  # Ensure non-negative
                    strike_damage += damage
                    damage_values.append(damage)
                except Exception as e:
                    # Skip this effector if distribution sampling fails
                    print(f"Warning: Failed to sample damage for effector: {e}")
                    continue
        
        # Update cumulative damage
        cumulative_total += strike_damage
        strikes.append(strike_num)
        cumulative_damage.append(cumulative_total)
    
    # Calculate min/max
    min_damage = min(damage_values) if damage_values else 0.0
    max_damage = max(damage_values) if damage_values else 0.0
    
    return {
        "strikes": strikes,
        "cumulative_damage": cumulative_damage,
        "damage_values": damage_values,
        "min_damage": min_damage,
        "max_damage": max_damage,
    }


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
        min_val = params.get("min_val", 0.0)
        max_val = params.get("max_val", 1.0)
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

