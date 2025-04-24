"""
Interface registry for the AeroLearn AI system.

This module provides a registry for component interfaces, ensuring components
properly implement required interfaces and allowing for interface discovery.
"""
import inspect
import logging
from typing import Dict, List, Set, Any, Optional, Type, Callable, get_type_hints

from ..events.event_bus import EventBus
from ..events.event_types import Event, EventCategory, EventPriority

logger = logging.getLogger(__name__)


class InterfaceDefinitionError(Exception):
    """Exception raised when an interface is improperly defined."""
    pass


class InterfaceImplementationError(Exception):
    """Exception raised when an interface is improperly implemented."""
    pass


class Interface:
    """
    Base class for all interfaces in the system.
    
    Interfaces define the contract that components must fulfill to provide
    certain functionality to other components.
    """
    
    @classmethod
    def get_interface_name(cls) -> str:
        """Get the canonical name of this interface."""
        return f"{cls.__module__}.{cls.__name__}"
    
    @classmethod
    def get_interface_version(cls) -> str:
        """Get the version of this interface."""
        return getattr(cls, "VERSION", "1.0.0")
    
    @classmethod
    def get_required_methods(cls) -> Set[str]:
        """Get the set of method names that must be implemented."""
        methods = set()
        for name, member in inspect.getmembers(cls):
            if (inspect.isfunction(member) and 
                    not name.startswith('_') and
                    name != 'get_interface_name' and
                    name != 'get_interface_version' and
                    name != 'get_required_methods' and
                    name != 'validate_implementation'):
                methods.add(name)
        return methods
    
    @classmethod
    def validate_implementation(cls, implementation: Any) -> List[str]:
        """
        Validate that an object correctly implements this interface.
        
        Args:
            implementation: The object to validate
            
        Returns:
            List of validation errors, empty if valid
        """
        errors = []
        
        # Check required methods
        for method_name in cls.get_required_methods():
            if not hasattr(implementation, method_name):
                errors.append(f"Missing method: {method_name}")
                continue
            
            impl_method = getattr(implementation, method_name)
            if not callable(impl_method):
                errors.append(f"Attribute {method_name} is not callable")
                continue
            
            # Get reference method from interface
            ref_method = getattr(cls, method_name)
            
            # Check signature compatibility
            try:
                impl_sig = inspect.signature(impl_method)
                ref_sig = inspect.signature(ref_method)
                
                # Compare parameter counts (excluding self)
                impl_params = list(impl_sig.parameters.values())[1:]  # Skip self
                ref_params = list(ref_sig.parameters.values())[1:]    # Skip self
                
                if len(impl_params) < len(ref_params):
                    errors.append(f"Method {method_name} has too few parameters")
                
                # Check parameter names and types
                for i, ref_param in enumerate(ref_params):
                    if i >= len(impl_params):
                        break
                    
                    impl_param = impl_params[i]
                    
                    # Check names match (unless using *args or **kwargs)
                    if (impl_param.name != ref_param.name and
                            impl_param.kind not in (inspect.Parameter.VAR_POSITIONAL, 
                                                  inspect.Parameter.VAR_KEYWORD)):
                        errors.append(f"Parameter name mismatch in {method_name}: {impl_param.name} != {ref_param.name}")
                
                # Check return type annotation
                ref_return_type = ref_sig.return_annotation
                impl_return_type = impl_sig.return_annotation
                
                if (ref_return_type != inspect.Signature.empty and 
                        impl_return_type != inspect.Signature.empty and
                        ref_return_type != impl_return_type):
                    errors.append(f"Return type mismatch in {method_name}: {impl_return_type} != {ref_return_type}")
                
            except ValueError:
                errors.append(f"Could not inspect method signature: {method_name}")
        
        return errors


class InterfaceRegisteredEvent(Event):
    """Event fired when an interface is registered."""
    def __init__(self, interface_name: str, version: str):
        super().__init__(
            event_type="interface.registered",
            category=EventCategory.SYSTEM,
            source_component="component_registry",  # Add this line
            priority=EventPriority.NORMAL,
            data={
                "interface_name": interface_name,
                "version": version
            },
            is_persistent=True
        )


class InterfaceRegistry:
    """
    Registry for interfaces in the system.
    
    This class is implemented as a singleton to ensure there is only one
    interface registry in the application.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InterfaceRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the interface registry (only executed once due to Singleton pattern)."""
        if self._initialized:
            return
        
        self._interfaces: Dict[str, Type[Interface]] = {}
        self._interface_versions: Dict[str, str] = {}
        self._event_bus: Optional[EventBus] = None
        self._stats: Dict[str, Any] = {
            "total_interfaces": 0
        }
        self._initialized = True
    
    async def initialize(self) -> None:
        """Initialize the interface registry."""
        self._event_bus = EventBus()
        logger.info("Interface registry initialized")
    
    def register_interface(self, interface_cls: Type[Interface]) -> bool:
        """
        Register an interface with the registry.
        
        Args:
            interface_cls: The interface class to register
            
        Returns:
            True if registration successful, False otherwise
            
        Raises:
            InterfaceDefinitionError: If the interface is improperly defined
        """
        # Validate interface class extends Interface
        if not issubclass(interface_cls, Interface):
            raise InterfaceDefinitionError(f"Class {interface_cls.__name__} does not extend Interface")
        
        interface_name = interface_cls.get_interface_name()
        interface_version = interface_cls.get_interface_version()
        
        # Check if already registered
        if interface_name in self._interfaces:
            existing_version = self._interface_versions[interface_name]
            if existing_version == interface_version:
                logger.warning(f"Interface already registered: {interface_name} (version {interface_version})")
                return False
            else:
                logger.warning(
                    f"Replacing interface {interface_name} version {existing_version} with version {interface_version}"
                )
        
        # Register the interface
        self._interfaces[interface_name] = interface_cls
        self._interface_versions[interface_name] = interface_version
        self._stats["total_interfaces"] = len(self._interfaces)
        
        # Publish event
        if self._event_bus:
            event = InterfaceRegisteredEvent(interface_name, interface_version)
            import asyncio
            asyncio.create_task(self._event_bus.publish(event))
        
        logger.info(f"Interface registered: {interface_name} (version {interface_version})")
        return True
    
    def get_interface(self, interface_name: str) -> Optional[Type[Interface]]:
        """
        Get an interface by name.
        
        Args:
            interface_name: The name of the interface to get
            
        Returns:
            The interface class if found, None otherwise
        """
        return self._interfaces.get(interface_name)
    
    def get_interface_version(self, interface_name: str) -> Optional[str]:
        """
        Get the version of an interface.
        
        Args:
            interface_name: The name of the interface to get the version for
            
        Returns:
            The version string if found, None otherwise
        """
        return self._interface_versions.get(interface_name)
    
    def get_all_interfaces(self) -> Dict[str, Type[Interface]]:
        """
        Get all registered interfaces.
        
        Returns:
            Dictionary mapping interface names to interface classes
        """
        return self._interfaces.copy()
    
    def validate_implementation(self, interface_name: str, implementation: Any) -> List[str]:
        """
        Validate that an object correctly implements an interface.
        
        Args:
            interface_name: The name of the interface to validate against
            implementation: The object to validate
            
        Returns:
            List of validation errors, empty if valid
            
        Raises:
            ValueError: If the interface is not found
        """
        interface_cls = self.get_interface(interface_name)
        if not interface_cls:
            raise ValueError(f"Interface not found: {interface_name}")
        
        return interface_cls.validate_implementation(implementation)
    
    def create_interface_documentation(self, interface_name: str) -> Dict[str, Any]:
        """
        Generate documentation for an interface.
        
        Args:
            interface_name: The name of the interface to document
            
        Returns:
            Dictionary containing interface documentation
            
        Raises:
            ValueError: If the interface is not found
        """
        interface_cls = self.get_interface(interface_name)
        if not interface_cls:
            raise ValueError(f"Interface not found: {interface_name}")
        
        docs = {
            "name": interface_name,
            "version": self.get_interface_version(interface_name),
            "description": interface_cls.__doc__ or "No description available",
            "methods": []
        }
        
        # Document methods
        for method_name in interface_cls.get_required_methods():
            method = getattr(interface_cls, method_name)
            sig = inspect.signature(method)
            
            method_doc = {
                "name": method_name,
                "description": method.__doc__ or "No description available",
                "parameters": [],
                "return_type": str(sig.return_annotation) if sig.return_annotation != inspect.Signature.empty else "unspecified"
            }
            
            # Document parameters
            params = list(sig.parameters.values())
            if params:
                # Skip 'self' parameter
                for param in params[1:]:
                    param_doc = {
                        "name": param.name,
                        "type": str(param.annotation) if param.annotation != inspect.Signature.empty else "unspecified",
                        "default": str(param.default) if param.default != inspect.Parameter.empty else None
                    }
                    method_doc["parameters"].append(param_doc)
            
            docs["methods"].append(method_doc)
        
        return docs
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the interface registry."""
        return self._stats.copy()


def implements(interface_cls: Type[Interface]) -> Callable:
    """
    Decorator to mark a class as implementing an interface.
    
    This decorator validates that the class correctly implements the interface
    and registers this information with the component registry.
    
    Args:
        interface_cls: The interface class that is implemented
        
    Returns:
        Decorator function
        
    Raises:
        InterfaceImplementationError: If the class does not correctly implement the interface
    """
    def decorator(cls):
        errors = interface_cls.validate_implementation(cls)
        if errors:
            error_str = "\n  - ".join([""] + errors)
            raise InterfaceImplementationError(
                f"Class {cls.__name__} does not correctly implement interface {interface_cls.get_interface_name()}:{error_str}"
            )
        
        # Store implemented interfaces in class metadata
        if not hasattr(cls, '_implemented_interfaces'):
            cls._implemented_interfaces = set()
        cls._implemented_interfaces.add(interface_cls.get_interface_name())
        
        # Return the original class
        return cls
    
    return decorator
