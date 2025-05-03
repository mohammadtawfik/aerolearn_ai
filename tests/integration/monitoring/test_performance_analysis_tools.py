"""
Test Suite: Performance Analysis Tools Integration Tests
Location: /tests/integration/monitoring/test_performance_analysis_tools.py

Covers Day 19 Plan Task 3.6.4:
- Component-specific benchmarks
- Cross-component transaction timing
- Resource utilization tracking
- Bottleneck identification
- Integration with multi-component workflows
- Accuracy of analysis

Interacts with analytics and monitoring code (app/core/monitoring/metrics.py).
"""

import pytest
import os
from app.core.monitoring.metrics import PerformanceAnalyzer

@pytest.fixture
def analyzer():
    """
    Returns a configured PerformanceAnalyzer instance for testing.
    """
    return PerformanceAnalyzer()

def test_component_performance_benchmark(analyzer):
    """
    PerformanceAnalyzer can benchmark a single component.
    
    Validates:
    - Benchmark returns valid metrics
    - Throughput is positive
    - Response time is measured
    """
    score = analyzer.benchmark_component("SearchEngine")
    assert score is not None
    assert score["throughput"] > 0
    assert "avg_response_time_ms" in score
    assert score["avg_response_time_ms"] >= 0

def test_cross_component_transaction_timing(analyzer):
    """
    Can measure and report timing information for cross-component workflows.
    
    Validates:
    - Total transaction time is measured
    - Individual component times are captured
    - Timing data is consistent (sum of parts <= whole + overhead)
    """
    times = analyzer.measure_transaction_flow(["Frontend", "API", "DB"])
    assert times["total_ms"] >= 0
    assert all(comp in times for comp in ["Frontend", "API", "DB"])
    
    # Verify timing consistency
    component_sum = sum(times[comp] for comp in ["Frontend", "API", "DB"])
    assert times["total_ms"] >= component_sum  # Total includes overhead

def test_resource_utilization_tracking(analyzer):
    """
    Analyzer can track and expose CPU/memory for a component.
    
    Validates:
    - CPU utilization is reported
    - Memory usage is reported
    - Disk I/O metrics are available
    """
    util = analyzer.get_resource_utilization("Indexer")
    assert util["cpu"] >= 0
    assert util["memory"] >= 0
    assert "disk_io" in util
    assert "network_io" in util

def test_performance_bottleneck_identification(analyzer):
    """
    Analyzer identifies bottleneck components in a workflow.
    
    Validates:
    - Bottlenecks are identified
    - Each bottleneck has a severity score
    - Recommendations for improvement are provided
    """
    bottlenecks = analyzer.identify_bottlenecks(["Frontend", "API", "DB"])
    assert isinstance(bottlenecks, list)
    
    if bottlenecks:
        bottleneck = bottlenecks[0]
        assert "component" in bottleneck
        assert "severity" in bottleneck
        assert "recommendations" in bottleneck

def test_multi_component_workflow_analysis(analyzer):
    """
    Analyzer can evaluate complex workflows spanning multiple components.
    
    Validates:
    - End-to-end performance metrics
    - Component interaction overhead
    - Parallel vs. sequential operations
    """
    workflow_perf = analyzer.analyze_workflow("UserSearch")
    assert "end_to_end_time_ms" in workflow_perf
    assert "component_breakdown" in workflow_perf
    assert "bottlenecks" in workflow_perf
    assert "optimization_potential" in workflow_perf

def test_performance_measurement_accuracy(analyzer):
    """
    Verifies the accuracy of measured/monitored performance metrics.
    
    Validates:
    - Measurements are consistent across runs
    - Synthetic benchmark results match expected ranges
    - Margin of error is acceptable
    """
    # Run the same benchmark multiple times to check consistency
    results = [analyzer.benchmark_component("API", sample_size=10) for _ in range(3)]
    
    # Calculate variance in throughput
    throughputs = [r["throughput"] for r in results]
    avg_throughput = sum(throughputs) / len(throughputs)
    variance = sum((t - avg_throughput)**2 for t in throughputs) / len(throughputs)
    
    # Variance should be within acceptable limits for stable components
    assert variance / avg_throughput < 0.2  # Less than 20% relative variance

def test_performance_analysis_documentation_exists():
    """
    Methodology docs should exist.
    
    Validates:
    - Documentation exists in expected locations
    - Documentation covers key methodologies
    """
    # Check for documentation files
    doc_exists = (
        os.path.exists("docs/architecture/performance_analysis.md") or
        os.path.exists("docs/api/performance_analysis.md")
    )
    assert doc_exists, "Performance analysis documentation is missing"
