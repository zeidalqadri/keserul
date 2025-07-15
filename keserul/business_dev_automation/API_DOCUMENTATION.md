# API Documentation

This document provides comprehensive API reference for the Business Development Automation System.

## 📋 Table of Contents

1. [Cost Manager API](#cost-manager-api)
2. [Prompt Optimization API](#prompt-optimization-api)
3. [System Coordinator API](#system-coordinator-api)
4. [Token Tracker API](#token-tracker-api)
5. [Prometheus Metrics API](#prometheus-metrics-api)
6. [Integration Testing API](#integration-testing-api)
7. [Business Development Bots API](#business-development-bots-api)

---

## 🏗️ Cost Manager API

### Core Functions

#### `get_cost_manager(enable_prometheus=True, prometheus_port=8000)`
Returns the global cost manager instance.

**Parameters:**
- `enable_prometheus` (bool): Enable Prometheus metrics export
- `prometheus_port` (int): Port for Prometheus metrics server

**Returns:** `CostManager` instance

**Example:**
```python
from shared.cost_manager import get_cost_manager

cm = get_cost_manager(enable_prometheus=True, prometheus_port=8000)
```

#### `start_cost_tracking(operation_name, metadata=None)`
Start tracking costs for a new operation.

**Parameters:**
- `operation_name` (str): Unique identifier for the operation
- `metadata` (dict, optional): Additional metadata for the operation

**Returns:** `CostReport` instance

**Example:**
```python
from shared.cost_manager import start_cost_tracking

report = start_cost_tracking(
    "prompt_optimization", 
    {"strategy": "orchestrator", "user": "dev"}
)
```

#### `track_api_cost(operation_name, response)`
Track an API call cost within an operation.

**Parameters:**
- `operation_name` (str): Operation identifier
- `response` (APIResponse): API response containing cost and token information

**Example:**
```python
from shared.cost_manager import track_api_cost
from archive.devin.cursorrules.tools.token_tracker import APIResponse, TokenUsage

api_response = APIResponse(
    content="Generated text",
    token_usage=TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
    cost=0.003,
    thinking_time=1.2,
    provider="openai",
    model="gpt-4"
)

track_api_cost("my_operation", api_response)
```

#### `complete_cost_tracking(operation_name)`
Complete cost tracking for an operation.

**Parameters:**
- `operation_name` (str): Operation identifier

**Returns:** `CostReport` instance or None

**Example:**
```python
from shared.cost_manager import complete_cost_tracking

final_report = complete_cost_tracking("my_operation")
print(f"Total cost: ${final_report.total_cost}")
print(f"Duration: {final_report.duration():.2f}s")
```

#### `track_metagpt_event(event_type, **kwargs)`
Track MetaGPT-specific events.

**Parameters:**
- `event_type` (str): Type of event ('optimization_cycle' or 'agent_action')
- `**kwargs`: Event-specific parameters

**Event Types:**
- `optimization_cycle`: Requires `strategy` and `status`
- `agent_action`: Requires `agent_type` and `status`

**Example:**
```python
from shared.cost_manager import track_metagpt_event

# Track optimization cycle
track_metagpt_event(
    'optimization_cycle',
    strategy='orchestrator',
    status='completed'
)

# Track agent action
track_metagpt_event(
    'agent_action',
    agent_type='PromptEngineer',
    status='prompt_generated'
)
```

### CostManager Class Methods

#### `start_operation(operation_name, metadata=None)`
Start a new cost tracking operation.

#### `track_api_call(operation_name, response)`
Track an API call within an operation.

#### `complete_operation(operation_name)`
Complete an operation and return the final cost report.

#### `get_operation_report(operation_name)`
Get current or completed report for an operation.

#### `get_session_summary()`
Get summary of all operations in the current session.

**Returns:**
```python
{
    'completed_operations': int,
    'active_operations': int,
    'total_cost': float,
    'total_tokens': int,
    'total_api_calls': int,
    'completed_cost': float,
    'active_cost': float,
    'prometheus_enabled': bool,
    'token_tracker_enabled': bool
}
```

### CostReport Class

#### Attributes
- `operation_name` (str): Name of the operation
- `start_time` (float): Start timestamp
- `end_time` (float): End timestamp (None if active)
- `total_cost` (float): Total cost in USD
- `total_tokens` (int): Total tokens used
- `api_calls` (int): Number of API calls
- `provider_costs` (dict): Cost breakdown by provider
- `provider_tokens` (dict): Token breakdown by provider
- `metadata` (dict): Additional metadata

#### Methods

#### `duration()`
Calculate operation duration in seconds.

**Returns:** float

#### `add_api_call(provider, cost, tokens)`
Add an API call to the cost report.

#### `finalize()`
Mark the operation as complete.

---

## 🧠 Prompt Optimization API

### Main Function

#### `optimize_prompt(original_prompt, strategy="orchestrator", use_legacy_cli=False, max_iterations=5)`
Optimize a prompt using MetaGPT agents or CLI strategy.

**Parameters:**
- `original_prompt` (str): The prompt to optimize
- `strategy` (str): Optimization strategy ("orchestrator" or "cli")
- `use_legacy_cli` (bool): Force CLI strategy usage
- `max_iterations` (int): Maximum optimization iterations

**Returns:** str (optimized prompt)

**Example:**
```python
from prompt_optimizer_bot.optimize_prompt import optimize_prompt

optimized = optimize_prompt(
    "Write a greeting message",
    strategy="orchestrator",
    max_iterations=3
)
print(f"Optimized prompt: {optimized}")
```

### Strategy-Specific Functions

#### `optimize_prompt_orchestrator(original_prompt, max_iterations=5)`
Use orchestrator strategy for optimization.

#### `optimize_prompt_cli(original_prompt, max_iterations=5)`
Use CLI strategy for optimization.

### Demo CLI Interface

**Command:**
```bash
python prompt_optimizer_bot/demo_cli.py [options]
```

**Options:**
- `--prompt` (str): Prompt to optimize
- `--strategy` (str): Strategy to use ("orchestrator" or "cli")
- `--use_legacy_cli`: Force CLI strategy
- `--max_iterations` (int): Maximum iterations
- `--info`: Show system information

**Example:**
```bash
python prompt_optimizer_bot/demo_cli.py \
    --prompt "Write a professional email" \
    --strategy orchestrator \
    --max_iterations 3
```

---

## 🎯 System Coordinator API

### Command Line Interface

**Command:**
```bash
python system_coordinator.py [options]
```

**Options:**
- `--optimize-prompts`: Enable prompt optimization
- `--input` (str): Input prompt or file
- `--strategy` (str): Optimization strategy
- `--max-iterations` (int): Maximum optimization iterations

**Examples:**
```bash
# Basic optimization
python system_coordinator.py --optimize-prompts --input "Hello world"

# With specific strategy
python system_coordinator.py \
    --optimize-prompts \
    --input "Write a report" \
    --strategy orchestrator \
    --max-iterations 5
```

### Python API

#### `main()`
Main entry point for system coordination.

#### Integration with Business Bots
The system coordinator orchestrates all business development bots and can invoke prompt optimization on their behalf.

---

## 📊 Token Tracker API

### Core Classes

#### `TokenUsage`
Data class for token usage information.

**Attributes:**
- `prompt_tokens` (int): Input prompt tokens
- `completion_tokens` (int): Response tokens
- `total_tokens` (int): Total tokens used
- `reasoning_tokens` (int, optional): Reasoning tokens (O1 model only)

#### `APIResponse`
Data class for API response information.

**Attributes:**
- `content` (str): Response content
- `token_usage` (TokenUsage): Token usage information
- `cost` (float): API call cost
- `thinking_time` (float): Response time
- `provider` (str): API provider
- `model` (str): Model used

### Main Functions

#### `get_token_tracker(session_id=None, logs_dir=None)`
Get or create global token tracker instance.

#### Cost Calculation Functions

#### `calculate_openai_cost(prompt_tokens, completion_tokens, model)`
Calculate cost for OpenAI models.

**Supported Models:**
- `o1`: $15/$60 per 1M tokens (input/output)
- `gpt-4o`: $10/$30 per 1M tokens (input/output)
- `deepseek-chat`: $0.2/$0.2 per 1M tokens (input/output)

#### `calculate_claude_cost(prompt_tokens, completion_tokens, model)`
Calculate cost for Claude models.

**Supported Models:**
- `claude-3-5-sonnet-20241022`: $3/$15 per 1M tokens (input/output)
- `claude-3-sonnet-20240229`: $3/$15 per 1M tokens (input/output)

### TokenTracker Class Methods

#### `track_request(response)`
Track a new API request.

#### `get_session_summary()`
Get session summary with costs and token usage.

---

## 📈 Prometheus Metrics API

### Available Metrics

#### Cost Metrics
- `llm_api_cost_total`: Total cost of LLM API calls
  - Labels: `provider`, `model`, `operation`
- `llm_api_tokens_total`: Total tokens used
  - Labels: `provider`, `model`, `operation`, `token_type`
- `llm_api_calls_total`: Total API calls
  - Labels: `provider`, `model`, `operation`

#### Performance Metrics
- `llm_operation_duration_seconds`: Operation duration histogram
  - Labels: `operation`
- `llm_active_operations`: Active operations gauge
  - Labels: `operation`

#### MetaGPT Metrics
- `metagpt_optimization_cycles_total`: Optimization cycles counter
  - Labels: `strategy`, `status`
- `metagpt_agent_actions_total`: Agent actions counter
  - Labels: `agent_type`, `action`

### Metrics Endpoint

**URL:** `http://localhost:8000/metrics`

**Format:** Prometheus exposition format

**Example Query:**
```bash
curl -s http://localhost:8000/metrics | grep llm_api_cost_total
```

---

## 🧪 Integration Testing API

### Test Execution Functions

#### Direct Execution
```python
python test_integration.py
```

#### Pytest Execution
```python
pytest test_integration.py -v
```

### Test Classes

#### `APIToCostManagerIntegration`
Tests API call tracking integration.

**Methods:**
- `test_api_call_tracking_basic()`
- `test_api_call_tracking_edge_cases()`

#### `CostManagerToPrometheusIntegration`
Tests metrics export to Prometheus.

**Methods:**
- `test_prometheus_metrics_creation()`
- `test_prometheus_metrics_accuracy()`

#### `PrometheusToGrafanaIntegration`
Tests Grafana dashboard compatibility.

**Methods:**
- `test_grafana_datasource_connectivity()`
- `test_grafana_dashboard_compatibility()`

#### `EndToEndDataFlow`
Tests complete data pipeline.

**Methods:**
- `test_complete_data_flow()`

#### `OptimizationWorkflowIntegration`
Tests prompt optimization with cost tracking.

**Methods:**
- `test_optimization_with_cost_tracking()`

### Test Utilities

#### `create_test_api_response(cost=0.003, tokens=200)`
Create test API response for testing.

#### `setup_test_environment()`
Setup test environment with cleanup.

#### `cleanup_test_environment()`
Clean up test artifacts.

---

## 🤖 Business Development Bots API

### Lead Generation Bot

**Module:** `leadgen_bot/`

**Functions:**
- Lead identification and scoring
- Prospect data enrichment
- Contact information validation

### Outreach Bot

**Module:** `outreach_bot/`

**Functions:**
- Email campaign automation
- LinkedIn outreach
- Personalization engine

### Insights Bot

**Module:** `insights_bot/`

**Functions:**
- Market research automation
- Competitive intelligence
- Trend analysis

### Strategy Bot

**Module:** `strategy_bot/`

**Functions:**
- Business strategy recommendations
- Market analysis
- Growth planning

### Perplexity Bot

**Module:** `perplexity_bot/`

**Functions:**
- Real-time market research
- Data aggregation
- Insight synthesis

---

## 🔗 Integration Patterns

### Cost Tracking Integration

All bots automatically integrate with cost tracking:

```python
from shared.cost_manager import start_cost_tracking, complete_cost_tracking

# Start operation tracking
report = start_cost_tracking("leadgen_analysis")

# ... bot operations with LLM calls ...

# Complete tracking
final_report = complete_cost_tracking("leadgen_analysis")
```

### Error Handling

Standard error handling pattern:

```python
try:
    # Operation logic
    result = perform_operation()
    return result
except Exception as e:
    logger.error(f"Operation failed: {e}")
    # Cleanup and fallback
    return fallback_result
finally:
    # Ensure cost tracking completion
    complete_cost_tracking(operation_name)
```

### Logging Integration

All components use structured logging:

```python
import logging

logger = logging.getLogger(__name__)
logger.info(f"Operation completed: {operation_name}")
logger.error(f"Operation failed: {error_message}")
```

---

## 📚 Common Usage Patterns

### Basic Cost Tracking Workflow

```python
from shared.cost_manager import get_cost_manager
from archive.devin.cursorrules.tools.llm_api import query_llm

# Initialize cost manager
cm = get_cost_manager()

# Start operation
report = cm.start_operation("my_analysis")

# Perform LLM operations (automatically tracked)
response = query_llm("Analyze this data", provider="openai")

# Complete operation
final_report = cm.complete_operation("my_analysis")

print(f"Analysis cost: ${final_report.total_cost:.6f}")
print(f"Tokens used: {final_report.total_tokens}")
```

### Prompt Optimization Workflow

```python
from prompt_optimizer_bot.optimize_prompt import optimize_prompt

# Basic optimization
original = "Write a summary"
optimized = optimize_prompt(original, strategy="orchestrator")

print(f"Original: {original}")
print(f"Optimized: {optimized}")
```

### Integration Testing Workflow

```python
# Run all integration tests
import subprocess

result = subprocess.run(["python", "test_integration.py"], capture_output=True)
print(f"Tests {'PASSED' if result.returncode == 0 else 'FAILED'}")
```

---

## 🚨 Error Codes and Responses

### Common Error Codes

- `ImportError`: Missing dependencies
- `ValueError`: Invalid parameters
- `ConnectionError`: Network connectivity issues
- `APIError`: LLM provider errors
- `ConfigError`: Configuration issues

### Error Response Format

```python
{
    "error": "error_type",
    "message": "Human readable error message",
    "details": {
        "component": "cost_manager",
        "operation": "start_operation",
        "timestamp": "2024-01-15T10:30:00Z"
    }
}
```

---

## 🔧 Configuration Reference

### Environment Variables

Required for API functionality:

```bash
# LLM Providers
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DEEPSEEK_API_KEY=your_deepseek_key

# Monitoring
PROMETHEUS_PORT=8000
GRAFANA_PORT=3000

# Optional
AZURE_OPENAI_API_KEY=your_azure_key
GOOGLE_API_KEY=your_google_key
```

### Cost Manager Configuration

```python
# Custom configuration
cm = get_cost_manager(
    enable_prometheus=True,
    prometheus_port=8000
)
```

### Token Tracker Configuration

```python
# Custom session and logs directory
tracker = get_token_tracker(
    session_id="custom_session",
    logs_dir=Path("custom_logs")
)
```

---

## 📖 Examples and Tutorials

### Complete Integration Example

```python
from shared.cost_manager import get_cost_manager
from prompt_optimizer_bot.optimize_prompt import optimize_prompt
from archive.devin.cursorrules.tools.llm_api import query_llm

# Initialize system
cm = get_cost_manager()

# Start comprehensive operation
report = cm.start_operation("business_analysis", {
    "user": "analyst",
    "project": "market_research"
})

# Optimize prompt
original_prompt = "Analyze the current market trends"
optimized_prompt = optimize_prompt(original_prompt, strategy="orchestrator")

# Use optimized prompt
analysis = query_llm(optimized_prompt, provider="openai", model="gpt-4o")

# Complete operation
final_report = cm.complete_operation("business_analysis")

# Display results
print(f"Analysis: {analysis}")
print(f"Total Cost: ${final_report.total_cost:.6f}")
print(f"Tokens Used: {final_report.total_tokens}")
print(f"Duration: {final_report.duration():.2f}s")
```

For more examples and detailed tutorials, see the [Developer Guide](DEVELOPER_GUIDE.md) and [README](README.md). 