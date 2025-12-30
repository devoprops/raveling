"""Process effector classes."""

from typing import Dict, Any, Optional, Callable, List
from src.models.effectors.base import Effector


class ProcessEffector(Effector):
    """
    Process effector with customized function for input/output chains.
    
    These are customized effectors that can execute complex chains of operations.
    The process function takes character and target as inputs and returns results.
    
    Attributes:
        process_function: Custom function that executes the process
        process_config: Configuration dictionary for the process
        input_effectors: List of effector names that provide input to this process
        output_effectors: List of effector names that receive output from this process
    """
    
    def __init__(
        self,
        effector_name: str,
        process_function: Optional[Callable] = None,
        process_config: Optional[Dict[str, Any]] = None,
        input_effectors: Optional[List[str]] = None,
        output_effectors: Optional[List[str]] = None,
    ):
        """
        Initialize a process effector.
        
        Args:
            effector_name: Name/identifier for this effector
            process_function: Custom function that executes the process
            process_config: Configuration dictionary for the process
            input_effectors: List of effector names that provide input
            output_effectors: List of effector names that receive output
        """
        super().__init__(
            effector_type="process",
            effector_name=effector_name,
        )
        self.process_function = process_function
        self.process_config = process_config or {}
        self.input_effectors = input_effectors or []
        self.output_effectors = output_effectors or []
    
    def execute(self, character: Any, target: Any) -> Dict[str, Any]:
        """
        Execute the process.
        
        Args:
            character: Character using the item/skill
            target: Target character or object
            
        Returns:
            Dictionary with process execution results
        """
        if self.process_function:
            try:
                result = self.process_function(character, target, self.process_config)
                if isinstance(result, dict):
                    result["effector_type"] = "process"
                    result["effector_name"] = self.effector_name
                    return result
                else:
                    return {
                        "effector_type": "process",
                        "effector_name": self.effector_name,
                        "result": result,
                    }
            except Exception as e:
                return {
                    "effector_type": "process",
                    "effector_name": self.effector_name,
                    "error": str(e),
                }
        
        # Default: return configuration
        return {
            "effector_type": "process",
            "effector_name": self.effector_name,
            "process_config": self.process_config,
            "input_effectors": self.input_effectors,
            "output_effectors": self.output_effectors,
        }
    
    def to_config(self) -> Dict[str, Any]:
        """Convert effector to configuration dictionary."""
        config = {
            "effector_type": self.effector_type,
            "effector_name": self.effector_name,
            "process_config": self.process_config,
            "input_effectors": self.input_effectors,
            "output_effectors": self.output_effectors,
        }
        # Note: process_function cannot be serialized directly
        # It would need to be referenced by name or stored as code string
        if hasattr(self.process_function, "__name__"):
            config["process_function_name"] = self.process_function.__name__
        return config
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'ProcessEffector':
        """Create effector from configuration dictionary."""
        # Process function would need to be loaded from a registry or module
        # This is a placeholder - actual implementation would need function registry
        process_function = None
        if "process_function_name" in config:
            # Would look up function from registry
            pass
        
        return cls(
            effector_name=config["effector_name"],
            process_function=process_function,
            process_config=config.get("process_config", {}),
            input_effectors=config.get("input_effectors", []),
            output_effectors=config.get("output_effectors", []),
        )
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get tunable parameters."""
        params = super().get_parameters()
        params.update({
            "process_config": self.process_config,
            "input_effectors": self.input_effectors,
            "output_effectors": self.output_effectors,
        })
        return params

