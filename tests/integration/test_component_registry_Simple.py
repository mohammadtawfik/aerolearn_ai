# --- UNIVERSAL PROJECT ROOT IMPORT PATCH ---
import os
import sys

def _add_project_root_to_syspath():
    here = os.path.abspath(os.path.dirname(__file__))
    root = here
    while root and not (os.path.isdir(os.path.join(root, "app")) and os.path.isdir(os.path.join(root, "tests"))):
        parent = os.path.dirname(root)
        if parent == root: break
        root = parent
    if root not in sys.path:
        sys.path.insert(0, root)
_add_project_root_to_syspath()
# --- END PATCH ---

"""
Simplified Spyder-compatible tests for the Component Registry system without events.
"""
import asyncio
import logging
import sys
import os
from typing import List, Dict, Any, Optional

# Add project root to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Import only the registry components
from integrations.registry.component_registry import ComponentRegistry, Component, ComponentState

# Create a simple test component
class TestComponent(Component):
    """Test component for registry tests."""
    
    def __init__(self, component_id: str, version: str = "1.0.0"):
        super().__init__(component_id, "test_component", version)
        # Add lifecycle tracking attributes
        self.initialize_called = False
        self.start_called = False
        self.stop_called = False
    
    async def initialize(self):
        """Override to track calls"""
        self.initialize_called = True
        # Call parent method if it exists
        if hasattr(super(), "initialize"):
            return await super().initialize()
        return True
    
    async def start(self):
        """Override to track calls"""
        self.start_called = True
        # Call parent method if it exists
        if hasattr(super(), "start"):
            return await super().start()
        return True
    
    async def stop(self):
        """Override to track calls"""
        self.stop_called = True
        # Call parent method if it exists
        if hasattr(super(), "stop"):
            return await super().stop()
        return True

# Global variables
registry = None

# Helper method to safely call methods that might have different names
def safe_call(obj, primary_method, fallback_method, *args, **kwargs):
    """Call primary_method if it exists, otherwise try fallback_method"""
    if hasattr(obj, primary_method):
        method = getattr(obj, primary_method)
        return method(*args, **kwargs)
    elif hasattr(obj, fallback_method):
        method = getattr(obj, fallback_method)
        return method(*args, **kwargs)
    else:
        raise AttributeError(f"Object {obj} has neither {primary_method} nor {fallback_method} method")

async def setup_test():
    """Set up test environment"""
    global registry
    
    # Clear the singleton instance
    if hasattr(ComponentRegistry, "_instance"):
        ComponentRegistry._instance = None
    
    # Create registry
    registry = ComponentRegistry()
    
    # Initialize registry if it has such method
    if hasattr(registry, "initialize"):
        try:
            # Try as async method first
            return await registry.initialize()
        except (TypeError, AttributeError):
            # Try as sync method
            return registry.initialize()
    
    return True

async def test_component_registration():
    """Test basic component registration without events"""
    global registry
    print("Testing basic component registration (no events)...")
    
    try:
        # Create components
        component1 = TestComponent("test1")
        component2 = TestComponent("test2", "2.0.0")
        
        # Register components
        print("Registering components...")
        safe_call(registry, "register_component", "register", component1)
        safe_call(registry, "register_component", "register", component2)
        
        # Get components
        print("Getting components...")
        found1 = safe_call(registry, "get_component", "get", "test1")
        found2 = safe_call(registry, "get_component", "get", "test2")
        
        # Check results
        print(f"Component test1 found: {found1 is component1}")
        print(f"Component test2 found: {found2 is component2}")
        
        # Get by type
        print("Getting components by type...")
        components_by_type = None
        try:
            components_by_type = safe_call(registry, "get_components_by_type", "get_by_type", "test_component")
            print(f"Components by type found: {len(components_by_type) if components_by_type else 0}")
        except Exception as e:
            print(f"Error getting components by type: {e}")
        
        # Overall result
        result = (found1 is component1) and (found2 is component2)
        print(f"Basic registration test {'passed' if result else 'failed'}")
        return result
    
    except Exception as e:
        print(f"Error during component registration test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_component_lifecycle():
    """Test component lifecycle operations"""
    global registry
    print("\nTesting component lifecycle...")
    
    try:
        # Create a component
        component = TestComponent("lifecycle_test")
        
        # Register the component
        safe_call(registry, "register_component", "register", component)
        
        # Initialize component
        print("Initializing component...")
        initialize_result = False
        try:
            if hasattr(registry, "initialize_component"):
                initialize_result = await registry.initialize_component("lifecycle_test")
            else:
                print("Registry doesn't have initialize_component method")
                # Try alternative methods
                try:
                    initialize_result = await registry.initialize("lifecycle_test")
                except AttributeError:
                    print("No initialization method found on registry")
        except Exception as e:
            print(f"Error during initialization: {e}")
        
        # Start component
        print("Starting component...")
        start_result = False
        try:
            if hasattr(registry, "start_component"):
                start_result = await registry.start_component("lifecycle_test")
            else:
                print("Registry doesn't have start_component method")
                # Try alternative methods
                try:
                    start_result = await registry.start("lifecycle_test")
                except AttributeError:
                    print("No start method found on registry")
        except Exception as e:
            print(f"Error during start: {e}")
        
        # Stop component
        print("Stopping component...")
        stop_result = False
        try:
            if hasattr(registry, "stop_component"):
                stop_result = await registry.stop_component("lifecycle_test")
            else:
                print("Registry doesn't have stop_component method")
                # Try alternative methods
                try:
                    stop_result = await registry.stop("lifecycle_test")
                except AttributeError:
                    print("No stop method found on registry")
        except Exception as e:
            print(f"Error during stop: {e}")
        
        # Check component lifecycle state
        print(f"Component initialize called: {component.initialize_called}")
        print(f"Component start called: {component.start_called}")
        print(f"Component stop called: {component.stop_called}")
        
        # Check component state
        if hasattr(component, "state"):
            print(f"Component state: {component.state}")
        
        # Return overall result
        result = component.initialize_called and component.start_called and component.stop_called
        print(f"Lifecycle test {'passed' if result else 'failed'}")
        return result
    except Exception as e:
        print(f"Error during lifecycle test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_minimal_tests():
    """Run minimal tests without event dependencies"""
    print("Running minimal Component Registry tests in Spyder...\n")
    
    try:
        await setup_test()
        
        # Run registration test
        reg_result = await test_component_registration()
        
        # Run lifecycle test
        life_result = await test_component_lifecycle()
        
        # Show overall results
        print("\nTEST SUMMARY")
        print("============")
        print(f"Registration Test: {'PASS' if reg_result else 'FAIL'}")
        print(f"Lifecycle Test:    {'PASS' if life_result else 'FAIL'}")
        print(f"Overall:          {'PASS' if reg_result and life_result else 'FAIL'}")
        
    except Exception as e:
        print(f"Error during tests: {e}")
        import traceback
        traceback.print_exc()

# For Spyder execution guidance
print("To run minimal tests in Spyder, execute:")
print("await run_minimal_tests()")
