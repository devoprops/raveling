"""Base effector classes for item and skill effects."""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from src.utils.common.distributions import DistributionFunction


class Effector(ABC):
    """
    Base class for effectors in items and skills.
    
    Effectors represent configurable effects that can be applied when an item
    or skill is used. They carry configuration and parameters that can be
    easily tuned and stored in YAML configs and databases.
    
    Attributes:
        effector_type: Type of effector (damage, regenerative, buff, debuff, process)
        effector_name: Name/identifier for this effector instance
    """
    
    def __init__(
        self,
        effector_type: str,
        effector_name: str,
    ):
        """
        Initialize an effector.
        
        Args:
            effector_type: Type of effector (must be a valid effector type)
            effector_name: Name/identifier for this effector instance
        """
        self.effector_type = effector_type
        self.effector_name = effector_name
    
    @abstractmethod
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the effector and return results.
        
        Args:
            character: Character using the item/skill
            target: Target character or object
            
        Returns:
            Dictionary containing effect results (varies by effector type)
        """
        pass
    
    @abstractmethod
    def to_config(self) -> Dict[str, Any]:
        """
        Convert effector to configuration dictionary for YAML/database storage.
        
        Returns:
            Dictionary representation of effector configuration
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_config(cls, config: Dict[str, Any]) -> 'Effector':
        """
        Create effector instance from configuration dictionary.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Effector instance
        """
        pass
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get tunable parameters for this effector.
        
        Returns:
            Dictionary of parameter names and their current values
        """
        return {
            "effector_type": self.effector_type,
            "effector_name": self.effector_name,
        }

