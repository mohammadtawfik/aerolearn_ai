import pytest

from integrations.registry.component_registry import ComponentRegistry
from integrations.registry.component import Component

class DummyComponent(Component):
    def __init__(self, component_id, version="1.0"):
        super().__init__(component_id)
        self._name = component_id
        self._version = version
        self.initialized = False
        self.started = False
        self.stopped = False

    async def initialize(self):
        self.initialized = True
        return True

    async def start(self):
        self.started = True
        return True

    async def stop(self):
        self.stopped = True
        return True

    def name(self):
        return self._name

    def version(self):
        return self._version

@pytest.mark.asyncio
async def test_component_lifecycle():
    """Test initialize, start, and stop lifecycle for a single component."""
    registry = ComponentRegistry()
    comp = DummyComponent("lifecycle_test")
    registry.register_component(comp)

    await registry.initialize_component(comp.get_id())
    assert comp.initialized
    await registry.start_component(comp.get_id())
    assert comp.started
    await registry.stop_component(comp.get_id())
    assert comp.stopped

@pytest.mark.asyncio
async def test_bulk_lifecycle_operations():
    """Test initializing, starting, stopping all components in bulk."""
    registry = ComponentRegistry()
    comps = [DummyComponent(f"comp_{i}") for i in range(3)]
    for comp in comps:
        registry.register_component(comp)

    await registry.initialize_all_components()
    await registry.start_all_components()
    await registry.stop_all_components()
    assert all(comp.initialized for comp in comps)
    assert all(comp.started for comp in comps)
    assert all(comp.stopped for comp in comps)
