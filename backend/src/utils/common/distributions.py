"""Probability distribution utility functions for damage models and statistical calculations."""

import random
from typing import Callable, Union, Dict
from collections import defaultdict


def sample_uniform(min_val: float, max_val: float) -> float:
    """
    Sample from a uniform distribution.
    
    Args:
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Random value between min_val and max_val (inclusive)
    """
    return random.uniform(min_val, max_val)


def sample_gaussian(mean: float, std_dev: float) -> float:
    """
    Sample from a Gaussian (normal) distribution.
    
    Args:
        mean: Mean of the distribution
        std_dev: Standard deviation
        
    Returns:
        Random value from normal distribution
    """
    return random.gauss(mean, std_dev)


def sample_skewnorm(mean: float, std_dev: float, skew: float) -> float:
    """
    Sample from a skewed normal distribution.
    
    Uses a simple approximation: generates normal samples and applies skew transformation.
    
    Args:
        mean: Mean of the distribution
        std_dev: Standard deviation
        skew: Skewness parameter (positive = right skew, negative = left skew)
        
    Returns:
        Random value from skewed normal distribution
    """
    # Simple skew transformation using exponential
    base_sample = random.gauss(mean, std_dev)
    # Apply skew: positive skew shifts distribution right
    if skew != 0:
        skew_factor = 1 + (skew * abs(base_sample - mean) / (std_dev + 1))
        return mean + (base_sample - mean) * skew_factor
    return base_sample


def sample_bimodal(
    mean1: float, std1: float, mean2: float, std2: float, weight: float
) -> float:
    """
    Sample from a bimodal distribution.
    
    Args:
        mean1: Mean of first mode
        std1: Standard deviation of first mode
        mean2: Mean of second mode
        std2: Standard deviation of second mode
        weight: Weight for first mode (0-1), second mode weight is (1-weight)
        
    Returns:
        Random value from bimodal distribution
    """
    if random.random() < weight:
        return random.gauss(mean1, std1)
    else:
        return random.gauss(mean2, std2)


def sample_die_roll(notation: str) -> int:
    """
    Sample from a die roll distribution (e.g., "2d5", "1d4", "3d6").
    
    Args:
        notation: Die notation string in format "NdM" where N is number of dice
                 and M is number of sides
        
    Returns:
        Sum of die rolls
        
    Raises:
        ValueError: If notation format is invalid
    """
    try:
        parts = notation.lower().split("d")
        if len(parts) != 2:
            raise ValueError(f"Invalid die notation: {notation}")
        
        num_dice = int(parts[0])
        num_sides = int(parts[1])
        
        if num_dice < 1 or num_sides < 1:
            raise ValueError(f"Invalid die notation: {notation}")
        
        total = 0
        for _ in range(num_dice):
            total += random.randint(1, num_sides)
        
        return total
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid die notation: {notation}") from e


def calculate_dice_probabilities(num_dice: int, num_sides: int) -> Dict[int, float]:
    """
    Calculate the exact probability distribution for rolling multiple dice.
    
    Uses dynamic programming to calculate all possible sums and their probabilities.
    
    Args:
        num_dice: Number of dice to roll
        num_sides: Number of sides on each die
        
    Returns:
        Dictionary mapping sum values to their probabilities
    """
    # Dictionary to store the counts of each possible sum
    # Keys are sums, values are the number of ways to get that sum
    ways_to_roll = defaultdict(int)
    ways_to_roll[0] = 1  # Start with one way to get a sum of 0 (by rolling 0 dice)
    
    # Iterate through each die
    for _ in range(num_dice):
        next_ways = defaultdict(int)
        # For each possible sum from previous dice rolls
        for current_sum, count in ways_to_roll.items():
            # Add each possible side of the new die
            for side in range(1, num_sides + 1):
                next_ways[current_sum + side] += count
        ways_to_roll = next_ways  # Update for the next iteration
    
    # Calculate total outcomes (num_sides^num_dice)
    total_outcomes = num_sides ** num_dice
    
    # Calculate probabilities
    probabilities = {}
    for sum_val, count in ways_to_roll.items():
        probabilities[sum_val] = count / total_outcomes
    
    return probabilities


# Type alias for distribution functions
DistributionFunction = Callable[[], Union[float, int]]


def create_distribution_function(distribution_params: Dict[str, Any]) -> DistributionFunction:
    """
    Create a distribution function from parameters dictionary.
    
    Args:
        distribution_params: Dictionary with 'type' and 'params' keys
            Example: {"type": "gaussian", "params": {"mean": 10.0, "std_dev": 2.0}}
    
    Returns:
        Distribution function that can be called to sample values
    """
    dist_type = distribution_params.get("type", "gaussian")
    params = distribution_params.get("params", {})
    
    if dist_type == "uniform":
        min_val = params.get("min", 0.0)
        max_val = params.get("max", 10.0)
        return lambda: sample_uniform(min_val, max_val)
    
    elif dist_type == "gaussian":
        mean = params.get("mean", 0.0)
        std_dev = params.get("std_dev", 1.0)
        return lambda: sample_gaussian(mean, std_dev)
    
    elif dist_type == "skewnorm":
        mean = params.get("mean", 0.0)
        std_dev = params.get("std_dev", 1.0)
        skew = params.get("skew", 0.0)
        return lambda: sample_skewnorm(mean, std_dev, skew)
    
    elif dist_type == "bimodal":
        mean1 = params.get("mean1", 0.0)
        std1 = params.get("std1", 1.0)
        mean2 = params.get("mean2", 10.0)
        std2 = params.get("std2", 1.0)
        weight = params.get("weight", 0.5)
        return lambda: sample_bimodal(mean1, std1, mean2, std2, weight)
    
    elif dist_type == "die_roll":
        notation = params.get("notation", "1d6")
        return lambda: sample_die_roll(notation)
    
    else:
        # Default to gaussian
        mean = params.get("mean", 0.0)
        std_dev = params.get("std_dev", 1.0)
        return lambda: sample_gaussian(mean, std_dev)

