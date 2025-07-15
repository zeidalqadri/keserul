"""
Cost Management System for Business Development Automation

Provides centralized cost tracking, Prometheus metrics, and reporting capabilities.
"""

import os
import sys
import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Add the archive tools to the path for token_tracker
sys.path.append(str(Path(__file__).parent.parent.parent / 'archive' / 'devin.cursorrules' / 'tools'))

try:
    from prometheus_client import Counter, Histogram, Gauge, start_http_server, CollectorRegistry, REGISTRY
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("Warning: Prometheus client not available. Metrics will not be exported.")

try:
    from token_tracker import get_token_tracker, TokenUsage, APIResponse, TokenTracker
    TOKEN_TRACKER_AVAILABLE = True
except ImportError:
    TOKEN_TRACKER_AVAILABLE = False
    print("Warning: Token tracker not available. Cost tracking will be limited.")
    # Create dummy classes for type hints when token_tracker is not available
    class APIResponse:
        def __init__(self, provider: str = "", cost: float = 0.0, token_usage: Any = None):
            self.provider = provider
            self.cost = cost
            self.token_usage = token_usage or type('TokenUsage', (), {'total_tokens': 0})()
    
    class TokenUsage:
        def __init__(self, total_tokens: int = 0):
            self.total_tokens = total_tokens
    
    TokenTracker = type('TokenTracker', (), {})

logger = logging.getLogger(__name__)

@dataclass
class CostReport:
    """Comprehensive cost report for a specific operation or session"""
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    total_cost: float = 0.0
    total_tokens: int = 0
    api_calls: int = 0
    provider_costs: Dict[str, float] = field(default_factory=dict)
    provider_tokens: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def duration(self) -> float:
        """Calculate operation duration in seconds"""
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time
    
    def add_api_call(self, provider: str, cost: float, tokens: int):
        """Add an API call to the cost report"""
        self.total_cost += cost
        self.total_tokens += tokens
        self.api_calls += 1
        
        self.provider_costs[provider] = self.provider_costs.get(provider, 0) + cost
        self.provider_tokens[provider] = self.provider_tokens.get(provider, 0) + tokens
    
    def finalize(self):
        """Mark the operation as complete"""
        self.end_time = time.time()

class CostManager:
    """Central cost management system with Prometheus integration"""
    
    def __init__(self, enable_prometheus: bool = True, prometheus_port: int = 8000):
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        self.prometheus_port = prometheus_port
        self.active_reports: Dict[str, CostReport] = {}
        self.completed_reports: Dict[str, CostReport] = {}
        
        # Initialize Prometheus metrics if available
        if self.enable_prometheus:
            self._setup_prometheus_metrics()
            self._start_prometheus_server()
        
        # Initialize token tracker if available
        if TOKEN_TRACKER_AVAILABLE:
            self.token_tracker = get_token_tracker()
        else:
            self.token_tracker = None
    
    def _setup_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        if not self.enable_prometheus:
            return
            
        # Cost metrics
        self.cost_counter = Counter(
            'llm_api_cost_total',
            'Total cost of LLM API calls',
            ['provider', 'model', 'operation']
        )
        
        self.token_counter = Counter(
            'llm_api_tokens_total',
            'Total tokens used in LLM API calls',
            ['provider', 'model', 'operation', 'token_type']
        )
        
        self.api_call_counter = Counter(
            'llm_api_calls_total',
            'Total number of LLM API calls',
            ['provider', 'model', 'operation']
        )
        
        self.operation_duration = Histogram(
            'llm_operation_duration_seconds',
            'Duration of LLM operations in seconds',
            ['operation']
        )
        
        self.active_operations = Gauge(
            'llm_active_operations',
            'Number of active LLM operations',
            ['operation']
        )
        
        # MetaGPT specific metrics
        self.metagpt_optimization_cycles = Counter(
            'metagpt_optimization_cycles_total',
            'Total number of MetaGPT optimization cycles',
            ['strategy', 'status']
        )
        
        self.metagpt_agent_actions = Counter(
            'metagpt_agent_actions_total',
            'Total number of MetaGPT agent actions',
            ['agent_type', 'action']
        )
        
        logger.info("Prometheus metrics initialized")
    
    def _start_prometheus_server(self):
        """Start Prometheus metrics server"""
        if not self.enable_prometheus:
            return
            
        try:
            start_http_server(self.prometheus_port)
            logger.info(f"Prometheus metrics server started on port {self.prometheus_port}")
        except Exception as e:
            logger.error(f"Failed to start Prometheus server: {e}")
            self.enable_prometheus = False
    
    def start_operation(self, operation_name: str, metadata: Optional[Dict[str, Any]] = None) -> CostReport:
        """Start tracking costs for a new operation"""
        if operation_name in self.active_reports:
            logger.warning(f"Operation {operation_name} already active. Completing previous operation.")
            self.complete_operation(operation_name)
        
        report = CostReport(
            operation_name=operation_name,
            start_time=time.time(),
            metadata=metadata or {}
        )
        
        self.active_reports[operation_name] = report
        
        # Update Prometheus metrics
        if self.enable_prometheus:
            self.active_operations.labels(operation=operation_name).inc()
        
        logger.info(f"Started cost tracking for operation: {operation_name}")
        return report
    
    def track_api_call(self, operation_name: str, response: APIResponse):
        """Track an API call within an operation"""
        if operation_name not in self.active_reports:
            logger.warning(f"No active operation {operation_name}. Starting new operation.")
            self.start_operation(operation_name)
        
        report = self.active_reports[operation_name]
        report.add_api_call(
            provider=response.provider,
            cost=response.cost,
            tokens=response.token_usage.total_tokens
        )
        
        # Track in token tracker if available
        if self.token_tracker:
            self.token_tracker.track_request(response)
        
        # Update Prometheus metrics
        if self.enable_prometheus:
            self.cost_counter.labels(
                provider=response.provider,
                model=response.model,
                operation=operation_name
            ).inc(response.cost)
            
            self.token_counter.labels(
                provider=response.provider,
                model=response.model,
                operation=operation_name,
                token_type='prompt'
            ).inc(response.token_usage.prompt_tokens)
            
            self.token_counter.labels(
                provider=response.provider,
                model=response.model,
                operation=operation_name,
                token_type='completion'
            ).inc(response.token_usage.completion_tokens)
            
            self.api_call_counter.labels(
                provider=response.provider,
                model=response.model,
                operation=operation_name
            ).inc()
        
        logger.debug(f"Tracked API call for {operation_name}: {response.provider} ${response.cost:.6f}")
    
    def track_metagpt_event(self, event_type: str, agent_type: Optional[str] = None, strategy: Optional[str] = None, 
                           status: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Track MetaGPT-specific events"""
        if not self.enable_prometheus:
            return
        
        if event_type == 'optimization_cycle':
            self.metagpt_optimization_cycles.labels(
                strategy=strategy or 'unknown',
                status=status or 'unknown'
            ).inc()
        
        elif event_type == 'agent_action':
            self.metagpt_agent_actions.labels(
                agent_type=agent_type or 'unknown',
                action=status or 'unknown'
            ).inc()
        
        logger.debug(f"Tracked MetaGPT event: {event_type} - {agent_type} - {strategy} - {status}")
    
    def complete_operation(self, operation_name: str) -> Optional[CostReport]:
        """Complete an operation and finalize its cost report"""
        if operation_name not in self.active_reports:
            logger.warning(f"No active operation {operation_name} to complete")
            return None
        
        report = self.active_reports.pop(operation_name)
        report.finalize()
        
        self.completed_reports[operation_name] = report
        
        # Update Prometheus metrics
        if self.enable_prometheus:
            self.active_operations.labels(operation=operation_name).dec()
            self.operation_duration.labels(operation=operation_name).observe(report.duration())
        
        logger.info(f"Completed operation {operation_name}: ${report.total_cost:.6f} in {report.duration():.2f}s")
        return report
    
    def get_operation_report(self, operation_name: str) -> Optional[CostReport]:
        """Get the current or completed report for an operation"""
        if operation_name in self.active_reports:
            return self.active_reports[operation_name]
        return self.completed_reports.get(operation_name)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of all operations in the current session"""
        total_cost = sum(report.total_cost for report in self.completed_reports.values())
        total_tokens = sum(report.total_tokens for report in self.completed_reports.values())
        total_calls = sum(report.api_calls for report in self.completed_reports.values())
        
        active_cost = sum(report.total_cost for report in self.active_reports.values())
        active_tokens = sum(report.total_tokens for report in self.active_reports.values())
        active_calls = sum(report.api_calls for report in self.active_reports.values())
        
        return {
            'completed_operations': len(self.completed_reports),
            'active_operations': len(self.active_reports),
            'total_cost': total_cost + active_cost,
            'total_tokens': total_tokens + active_tokens,
            'total_api_calls': total_calls + active_calls,
            'completed_cost': total_cost,
            'active_cost': active_cost,
            'prometheus_enabled': self.enable_prometheus,
            'token_tracker_enabled': TOKEN_TRACKER_AVAILABLE
        }

# Global cost manager instance
_cost_manager: Optional[CostManager] = None

def get_cost_manager(enable_prometheus: bool = True, prometheus_port: int = 8000) -> CostManager:
    """Get or create the global cost manager instance"""
    global _cost_manager
    if _cost_manager is None:
        _cost_manager = CostManager(enable_prometheus=enable_prometheus, prometheus_port=prometheus_port)
    return _cost_manager

# Convenience functions for common operations
def start_cost_tracking(operation_name: str, metadata: Optional[Dict[str, Any]] = None) -> CostReport:
    """Start cost tracking for an operation"""
    return get_cost_manager().start_operation(operation_name, metadata)

def track_api_cost(operation_name: str, response: APIResponse):
    """Track an API call cost"""
    get_cost_manager().track_api_call(operation_name, response)

def complete_cost_tracking(operation_name: str) -> Optional[CostReport]:
    """Complete cost tracking for an operation"""
    return get_cost_manager().complete_operation(operation_name)

def track_metagpt_event(event_type: str, **kwargs):
    """Track a MetaGPT event"""
    get_cost_manager().track_metagpt_event(event_type, **kwargs) 