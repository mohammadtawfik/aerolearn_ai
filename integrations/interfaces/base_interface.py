"""
Base interface definitions for the AeroLearn AI system.

This module provides the core interface contract infrastructure, including interface
registration, discovery, and method signature validation mechanisms. All specific
interfaces in the system should inherit from the base classes defined here.
"""
import abc
import inspect
import logging
from enum import Enum
from typing import Dict, Any, Type, Set, Optional, List, Callable, Tuple
import semver

from ..registry.component_registry import ComponentRegistry, Component
from ..events.event_bus import EventBus
from ..events.event_types import Event, EventCategory, EventPriority

logger = logging.getLogger(__name__)


class InterfaceVersion:
    """
    Helper class for managing interface versioning.
    
    This class follows semantic versioning principles where:
    - MAJOR version changes indicate incompatible API changes
    - MINOR version changes indicate backwards-compatible functionality additions
    - PATCH version changes indicate backwards-compatible bug fixes
    """
    
    def __init__(self, major: int, minor: int, patch: int):
        """
        Initialize an interface version.
        
        Args:
            major: Major version number (incompatible API changes)
            minor: Minor version number (backwards-compatible additions)
            patch: Patch version number (backwards-compatible fixes)
        """
        self.major = major
        self.minor = minor
        self.patch = patch
    
    def __str__(self) -> str:
        """Convert to string in semver format."""
        return f"{self.major}.{self.minor}.{self.patch}"
    
    @classmethod
    def from_string(cls, version_str: str) -> 'InterfaceVersion':
        """
        Create an InterfaceVersion from a version string.
        
        Args:
            version_str: Version string in semver format (e.g. "1.0.0")
            
        Returns:
            InterfaceVersion object
            
        Raises:
            ValueError: If the version string is invalid
        """
        try:
            parts = version_str.split('.')
            if len(parts) != 3:
                raise ValueError(f"Invalid version format: {version_str}")
            
            return cls(int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid version format: {version_str}") from e
    
    def is_compatible_with(self, other: 'InterfaceVersion') -> bool:
        """
        Check if this version is compatible with another version.
        
        Two versions are compatible if they have the same major version.
        
        Args:
            other: Version to compare with
            
        Returns:
            True if compatible, False otherwise
        """
        return self.major == other.major


class MethodSignature:
    """
    Class for representing and validating method signatures.
    
    This class captures the signature information of a method, including
    parameter types and return type annotations, to enable validation when
    implementing interfaces.
    """
    
    def __init__(self, method: Callable):
        """
        Initialize with a method to capture its signature.
        
        Args:
            method: The method to capture signature from
        """
        self.signature = inspect.signature(method)
        self.parameters = self.signature.parameters
        self.return_annotation = self.signature.return_annotation
    
    def validate_implementation(self, implementation: Callable) -> Tuple[bool, Optional[str]]:
        """
        Validate that an implementation matches this signature.
        
        Args:
            implementation: The implementation method to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            impl_sig = inspect.signature(implementation)
            
            # Check return type
            if (self.return_annotation != inspect.Signature.empty and
                    impl_sig.return_annotation != inspect.Signature.empty and
                    self.return_annotation != impl_sig.return_annotation):
                return False, f"Return type mismatch: expected {self.return_annotation}, got {impl_sig.return_annotation}"
            
            # Check parameters
            if len(self.parameters) != len(impl_sig.parameters):
                return False, f"Parameter count mismatch: expected {len(self.parameters)}, got {len(impl_sig.parameters)}"
            
            # Skip 'self' parameter in both signatures if present
            self_params = {'self', 'cls'}
            base_params = {name: param for name, param in self.parameters.items() if name not in self_params}
            impl_params = {name: param for name, param in impl_sig.parameters.items() if name not in self_params}
            
            if len(base_params) != len(impl_params):
                return False, f"Parameter count mismatch after excluding self/cls"
            
            # Check each parameter
            for name, param in base_params.items():
                if name not in impl_params:
                    return False, f"Missing parameter: {name}"
                
                impl_param = impl_params[name]
                
                # Check parameter type annotations
                if (param.annotation != inspect.Parameter.empty and
                        impl_param.annotation != inspect.Parameter.empty and
                        param.annotation != impl_param.annotation):
                    return False, f"Type mismatch for parameter {name}: expected {param.annotation}, got {impl_param.annotation}"
                
                # Check default values
                if param.default != impl_param.default:
                    if param.default == inspect.Parameter.empty and impl_param.default != inspect.Parameter.empty:
                        # It's okay to add a default value in the implementation
                        pass
                    elif param.default != inspect.Parameter.empty and impl_param.default == inspect.Parameter.empty:
                        return False, f"Implementation of {name} is missing default value"
            
            return True, None
        except Exception as e:
            return False, f"Error validating implementation: {str(e)}"


class InterfaceMethod:
    """
    Decorator for interface methods that captures signature information.
    """
    
    def __init__(self, func):
        """
        Initialize the decorator.
        
        Args:
            func: The method being decorated
        """
        self.func = func
        self.signature = MethodSignature(func)
    
    def __get__(self, obj, objtype=None):
        """
        Handle descriptor protocol for method access.
        
        This allows the decorated methods to be accessed either through
        the class or an instance.
        
        Args:
            obj: The object instance accessing this method
            objtype: The type of the object
            
        Returns:
            The original function
        """
        return self.func


class InterfaceError(Exception):
    """Base exception for interface-related errors."""
    pass


class InterfaceImplementationError(InterfaceError):
    """Exception raised when an interface is implemented incorrectly."""
    pass


class InterfaceRegistryError(InterfaceError):
    """Exception raised for interface registration errors."""
    pass


class InterfaceVersionError(InterfaceError):
    """Exception raised for interface version errors."""
    pass


class BaseInterface(abc.ABC):
    """
    Base class for all interface contracts in the system.
    """
    
    # Class-level registry of all interfaces
    _interfaces: Dict[str, Type['BaseInterface']] = {}
    _interface_versions: Dict[str, str] = {}
    _interface_descriptions: Dict[str, str] = {}
    
    # Interface identification
    interface_name: str = None
    interface_version: str = "0.0.0"
    interface_description: str = ""
    
    @classmethod
    def register_interface(cls) -> None:
        """
        Register this interface in the global interface registry.
        
        This should be called once for each interface class to make
        it discoverable by the system.
        
        Raises:
            InterfaceRegistryError: If the interface is already registered
                with a different version
        """
        if not cls.interface_name:
            raise InterfaceRegistryError(f"Interface {cls.__name__} has no interface_name defined")
        
        if cls.interface_name in cls._interfaces and cls._interfaces[cls.interface_name] != cls:
            # Check version compatibility if already registered
            existing_version = cls._interface_versions[cls.interface_name]
            if existing_version != cls.interface_version:
                existing_ver = InterfaceVersion.from_string(existing_version)
                new_ver = InterfaceVersion.from_string(cls.interface_version)
                
                if not existing_ver.is_compatible_with(new_ver):
                    raise InterfaceRegistryError(
                        f"Interface {cls.interface_name} already registered with incompatible version "
                        f"{existing_version} (attempting to register version {cls.interface_version})"
                    )
        
        cls._interfaces[cls.interface_name] = cls
        cls._interface_versions[cls.interface_name] = cls.interface_version
        cls._interface_descriptions[cls.interface_name] = cls.interface_description
        
        logger.info(f"Interface registered: {cls.interface_name} (version {cls.interface_version})")
    
    @classmethod
    def get_interface(cls, name: str) -> Optional[Type['BaseInterface']]:
        """
        Get an interface class by name.
        
        Args:
            name: Name of the interface to get
            
        Returns:
            Interface class if found, None otherwise
        """
        return cls._interfaces.get(name)
    
    @classmethod
    def get_all_interfaces(cls) -> Dict[str, Type['BaseInterface']]:
        """
        Get all registered interfaces.
        
        Returns:
            Dictionary mapping interface names to interface classes
        """
        return cls._interfaces.copy()
    
    @classmethod
    def get_interface_methods(cls) -> Dict[str, MethodSignature]:
        """
        Get all method signatures defined by this interface.
        
        Returns:
            Dictionary mapping method names to their signatures
        """
        methods = {}
        
        # Get all InterfaceMethod decorated methods
        for name, member in inspect.getmembers(cls):
            if isinstance(member, InterfaceMethod):
                methods[name] = member.signature
        
        return methods
    
    @classmethod
    def validate_implementation(cls, implementation_cls: Type) -> Tuple[bool, List[str]]:
        """
        Validate that a class correctly implements this interface.
        
        Args:
            implementation_cls: The class to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check that all interface methods are implemented
        interface_methods = cls.get_interface_methods()
        
        for method_name, signature in interface_methods.items():
            if not hasattr(implementation_cls, method_name):
                errors.append(f"Missing method implementation: {method_name}")
                continue
            
            impl_method = getattr(implementation_cls, method_name)
            if not callable(impl_method):
                errors.append(f"{method_name} is not callable")
                continue
            
            valid, error = signature.validate_implementation(impl_method)
            if not valid:
                errors.append(f"Invalid implementation of {method_name}: {error}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def interface_method(func):
        """
        Decorator for interface methods that captures signature information.
        
        This decorator should be used on all abstract methods in interface
        classes to enable signature validation.
        
        Args:
            func: The method being decorated
            
        Returns:
            InterfaceMethod wrapped around the original function
        """
        return InterfaceMethod(func)


class InterfaceImplementation:
    """
    Decorator for classes that implement interfaces.
    
    This decorator validates that a class correctly implements all
    the interfaces it claims to implement.
    """
    
    def __init__(self, *interfaces: Type[BaseInterface]):
        """
        Initialize with the interfaces to implement.
        
        Args:
            *interfaces: Interface classes that the decorated class implements
        """
        self.interfaces = interfaces
    
    def __call__(self, cls):
        """
        Validate and register class as implementing the interfaces.
        
        Args:
            cls: The class being decorated
            
        Returns:
            The original class
            
        Raises:
            InterfaceImplementationError: If the class doesn't correctly
                implement all required interfaces
        """
        for interface in self.interfaces:
            valid, errors = interface.validate_implementation(cls)
            
            if not valid:
                error_msg = f"Class {cls.__name__} does not correctly implement interface {interface.interface_name}:\n"
                error_msg += "\n".join(f"- {error}" for error in errors)
                raise InterfaceImplementationError(error_msg)
            
            # Register the implementation with the component (if applicable)
            if issubclass(cls, Component):
                cls.provide_interface(interface.interface_name, interface.interface_version)
        
        # Add list of implemented interfaces to the class
        cls._implemented_interfaces = self.interfaces
        
        return cls


# Interface registration event
class InterfaceRegisteredEvent(Event):
    """Event fired when an interface is registered."""
    def __init__(self, interface_name: str, version: str, description: str):
        super().__init__(
            event_type="interface.registered",
            category=EventCategory.SYSTEM,
            source_component="interface_registry",
            priority=EventPriority.NORMAL,
            data={
                "interface_name": interface_name,
                "version": version,
                "description": description
            },
            is_persistent=True
        )


def register_all_interfaces() -> None:
    """
    Register all interfaces defined in the system.
    
    This function scans all subclasses of BaseInterface and registers them.
    It should be called once during system initialization.
    """
    event_bus = EventBus()
    
    for interface_cls in BaseInterface.__subclasses__():
        try:
            interface_cls.register_interface()
            
            # Publish event for monitoring
            if hasattr(interface_cls, 'interface_name') and interface_cls.interface_name:
                event = InterfaceRegisteredEvent(
                    interface_cls.interface_name,
                    getattr(interface_cls, 'interface_version', "0.0.0"),
                    getattr(interface_cls, 'interface_description', "")
                )
                asyncio.create_task(event_bus.publish(event))
                
        except Exception as e:
            logger.error(f"Error registering interface {interface_cls.__name__}: {str(e)}")
    
    # Also check for any grandchildren classes that may define interfaces
    for parent in BaseInterface.__subclasses__():
        for interface_cls in parent.__subclasses__():
            if interface_cls.interface_name not in BaseInterface._interfaces:
                try:
                    interface_cls.register_interface()
                    
                    # Publish event for monitoring
                    if hasattr(interface_cls, 'interface_name') and interface_cls.interface_name:
                        event = InterfaceRegisteredEvent(
                            interface_cls.interface_name,
                            getattr(interface_cls, 'interface_version', "0.0.0"),
                            getattr(interface_cls, 'interface_description', "")
                        )
                        asyncio.create_task(event_bus.publish(event))
                        
                except Exception as e:
                    logger.error(f"Error registering interface {interface_cls.__name__}: {str(e)}")
