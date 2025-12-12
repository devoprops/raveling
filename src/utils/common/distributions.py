"""Probability distribution utility functions for damage models and statistical calculations."""

import random
from typing import Callable, Union


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


# Type alias for distribution functions
DistributionFunction = Callable[[], Union[float, int]]

