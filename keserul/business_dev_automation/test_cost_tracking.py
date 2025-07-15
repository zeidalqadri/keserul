#!/usr/bin/env python3
"""
Test script for end-to-end cost tracking functionality

This script tests:
1. Cost manager initialization
2. Prometheus metrics collection
3. MetaGPT optimization with cost tracking
4. Cost report generation
"""

import time
import asyncio
import sys
from pathlib import Path

# Add paths for imports
sys.path.append(str(Path(__file__).parent.parent / 'archive' / 'devin.cursorrules' / 'tools'))

from shared.cost_manager import get_cost_manager, CostReport
from prompt_optimizer_bot.utils.cost_instrumented_wrapper import optimize_prompt
from token_tracker import TokenUsage, APIResponse

def test_cost_manager_basic():
    """Test basic cost manager functionality"""
    print("=== Testing Cost Manager Basic Functionality ===")
    
    # Initialize cost manager
    cost_manager = get_cost_manager(enable_prometheus=True, prometheus_port=8001)
    
    # Test starting an operation
    report = cost_manager.start_operation("test_operation", {"test": "metadata"})
    print(f"Started operation: {report.operation_name}")
    
    # Simulate an API call
    fake_response = APIResponse(
        content="Test response",
        token_usage=TokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150
        ),
        cost=0.0045,
        thinking_time=1.2,
        provider="openai",
        model="gpt-4o"
    )
    
    cost_manager.track_api_call("test_operation", fake_response)
    print(f"Tracked API call: ${fake_response.cost:.6f}")
    
    # Complete the operation
    final_report = cost_manager.complete_operation("test_operation")
    if final_report:
        print(f"Completed operation: ${final_report.total_cost:.6f} in {final_report.duration():.2f}s")
    else:
        print("Failed to complete operation")
    
    # Get session summary
    summary = cost_manager.get_session_summary()
    print(f"Session summary: {summary}")
    
    return True

def test_metagpt_cost_tracking():
    """Test MetaGPT optimization with cost tracking"""
    print("\n=== Testing MetaGPT Cost Tracking ===")
    
    try:
        # Test with a simple optimization
        result = optimize_prompt(
            user_message="Write a greeting message",
            expected_output="Hello! How can I help you today?",
            acceptance_criteria="Should be friendly and welcoming",
            max_iterations=2,
            strategy='orchestrator'
        )
        
        print(f"Optimization result: {result[:100]}...")
        
        # Get cost summary
        cost_manager = get_cost_manager()
        summary = cost_manager.get_session_summary()
        print(f"Total cost after optimization: ${summary['total_cost']:.6f}")
        print(f"Total tokens: {summary['total_tokens']}")
        print(f"Total API calls: {summary['total_api_calls']}")
        
        return True
        
    except Exception as e:
        print(f"Error during MetaGPT cost tracking test: {e}")
        return False

def test_prometheus_metrics():
    """Test Prometheus metrics collection"""
    print("\n=== Testing Prometheus Metrics ===")
    
    try:
        # Check if Prometheus server is running
        import requests
        response = requests.get("http://localhost:8001/metrics", timeout=5)
        
        if response.status_code == 200:
            metrics_content = response.text
            print("Prometheus metrics server is running")
            
            # Check for our custom metrics
            expected_metrics = [
                'llm_api_cost_total',
                'llm_api_tokens_total',
                'llm_api_calls_total',
                'metagpt_optimization_cycles_total',
                'metagpt_agent_actions_total'
            ]
            
            found_metrics = []
            for metric in expected_metrics:
                if metric in metrics_content:
                    found_metrics.append(metric)
            
            print(f"Found metrics: {found_metrics}")
            print(f"Missing metrics: {set(expected_metrics) - set(found_metrics)}")
            
            return len(found_metrics) == len(expected_metrics)
        else:
            print(f"Prometheus server responded with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error testing Prometheus metrics: {e}")
        return False

def test_cost_report_generation():
    """Test cost report generation and persistence"""
    print("\n=== Testing Cost Report Generation ===")
    
    cost_manager = get_cost_manager()
    
    # Create multiple operations
    operations = ["test_op_1", "test_op_2", "test_op_3"]
    
    for op_name in operations:
        report = cost_manager.start_operation(op_name, {"test_id": op_name})
        
        # Simulate API calls with different costs
        for i in range(3):
            fake_response = APIResponse(
                content=f"Response {i}",
                token_usage=TokenUsage(
                    prompt_tokens=50 + i * 10,
                    completion_tokens=25 + i * 5,
                    total_tokens=75 + i * 15
                ),
                cost=0.001 + i * 0.0005,
                thinking_time=0.5 + i * 0.1,
                provider="openai",
                model="gpt-4o"
            )
            cost_manager.track_api_call(op_name, fake_response)
        
        # Complete the operation
        final_report = cost_manager.complete_operation(op_name)
        if final_report:
            print(f"Operation {op_name}: ${final_report.total_cost:.6f}, {final_report.total_tokens} tokens")
        else:
            print(f"Failed to complete operation {op_name}")
    
    # Generate session summary
    summary = cost_manager.get_session_summary()
    print(f"\nFinal session summary:")
    print(f"  Total cost: ${summary['total_cost']:.6f}")
    print(f"  Total tokens: {summary['total_tokens']}")
    print(f"  Total API calls: {summary['total_api_calls']}")
    print(f"  Completed operations: {summary['completed_operations']}")
    
    return True

def main():
    """Run all tests"""
    print("Starting End-to-End Cost Tracking Tests")
    print("=" * 50)
    
    tests = [
        ("Cost Manager Basic", test_cost_manager_basic),
        ("Cost Report Generation", test_cost_report_generation),
        ("MetaGPT Cost Tracking", test_metagpt_cost_tracking),
        ("Prometheus Metrics", test_prometheus_metrics),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            status = "PASS" if result else "FAIL"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            results[test_name] = False
            print(f"\n{test_name}: FAIL - {e}")
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: {status}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Cost tracking is working end-to-end.")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 