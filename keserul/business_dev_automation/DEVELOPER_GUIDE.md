# Developer Onboarding Guide

Welcome to the Business Development Automation System! This guide will help you get up to speed with our development environment, testing framework, and system architecture.

## 🎯 Quick Start for Developers

### 1. Development Environment Setup

**Prerequisites:**
- Python 3.9+ (3.11 recommended)
- Conda (preferred) or Python virtual environment
- Git
- Docker (for integration testing)
- Your favorite IDE (VS Code, PyCharm, etc.)

**Environment Setup:**
```bash
# Clone the repository
git clone <repository-url>
cd business_dev_automation

# Create conda environment (recommended)
conda env create -f environment.yml
conda activate business-dev-automation

# Alternative: pip virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Verify installation
python test_cost_tracking.py
python test_integration.py
```

### 2. Environment Configuration

**Copy and configure environment variables:**
```bash
cp .env.example .env
```

**Required API keys in .env:**
```bash
# Core LLM APIs (at least one required)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here

# Optional providers
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_MODEL_DEPLOYMENT=gpt-4o-ms
GOOGLE_API_KEY=your_google_key

# Development settings
PROMETHEUS_PORT=8000
GRAFANA_PORT=3000
```

### 3. First Run Verification

```bash
# Test core functionality
python test_cost_tracking.py

# Run comprehensive integration tests
python test_integration.py

# Test prompt optimization
python prompt_optimizer_bot/demo_cli.py --prompt "Hello world" --info
```

## 🧪 Testing Framework Deep Dive

### Testing Architecture

Our testing framework has three layers:

1. **Unit Tests**: Individual component testing with mocked dependencies
2. **Integration Tests**: End-to-end system component interaction testing
3. **CI/CD Tests**: Automated testing in GitHub Actions environment

### Integration Testing Framework

**File Structure:**
```
test_integration.py          # Main integration test suite
test_cost_tracking.py        # Cost tracking specific tests
.github/workflows/           # CI/CD pipeline definitions
environment.yml              # Conda environment specification
docker-compose.integration.yml  # Docker testing environment
```

**Key Test Classes:**

1. **APIToCostManagerIntegration**: Tests API call tracking
2. **CostManagerToPrometheusIntegration**: Tests metrics export
3. **PrometheusToGrafanaIntegration**: Tests monitoring stack
4. **EndToEndDataFlow**: Tests complete data pipeline
5. **OptimizationWorkflowIntegration**: Tests prompt optimization

### Running Tests

**Local Testing:**
```bash
# Run all integration tests
python test_integration.py

# Run with pytest (more detailed output)
pytest test_integration.py -v

# Run specific test class
pytest test_integration.py::APIToCostManagerIntegration -v

# Run cost tracking tests
python test_cost_tracking.py
```

**Docker Integration Testing:**
```bash
# Run tests in Docker environment
docker-compose -f docker-compose.integration.yml up --build

# Clean up after testing
docker-compose -f docker-compose.integration.yml down
```

**GitHub Actions (CI/CD):**
- Automatic testing on push/PR to main branch
- Tests run on Python 3.9, 3.10, 3.11
- Both conda and Docker environments tested
- Security scanning with Bandit and Safety

### Test Data and Mocking

**Test Data Generation:**
```python
# Example: Creating test API responses
from archive.devin.cursorrules.tools.token_tracker import TokenUsage, APIResponse

def create_test_api_response(cost=0.003, tokens=200):
    return APIResponse(
        content="Test response",
        token_usage=TokenUsage(
            prompt_tokens=100,
            completion_tokens=100,
            total_tokens=tokens
        ),
        cost=cost,
        thinking_time=1.0,
        provider="openai",
        model="gpt-4"
    )
```

**Mocking Guidelines:**
- Use `unittest.mock` for external API calls
- Mock expensive operations (LLM calls) in unit tests
- Use real integration for integration tests
- Always clean up test data

## 🏗️ System Architecture Understanding

### Core Components

1. **System Coordinator** (`system_coordinator.py`)
   - Central orchestration of all bots
   - CLI interface for system operations
   - Integration point for prompt optimization

2. **Cost Manager** (`shared/cost_manager.py`)
   - Centralized cost tracking
   - Prometheus metrics export
   - Session-based reporting

3. **Prompt Optimizer Bot** (`prompt_optimizer_bot/`)
   - MetaGPT integration for prompt optimization
   - Multi-strategy optimization (orchestrator/CLI)
   - Cost-aware optimization cycles

4. **Business Development Bots**
   - Lead Generation (`leadgen_bot/`)
   - Outreach Automation (`outreach_bot/`)
   - Market Insights (`insights_bot/`)
   - Strategy Development (`strategy_bot/`)

### Data Flow Architecture

```
User Input → System Coordinator → Business Bot → LLM API
                    ↓
              Cost Manager ← Token Tracker
                    ↓
              Prometheus Metrics → Grafana Dashboard
```

### Key Design Patterns

1. **Dependency Injection**: Cost manager injected into all components
2. **Observer Pattern**: Cost tracking observes all LLM operations
3. **Strategy Pattern**: Multiple optimization strategies (orchestrator/CLI)
4. **Factory Pattern**: LLM client creation based on provider
5. **Decorator Pattern**: Cost instrumentation wrapping

## 💡 Development Best Practices

### Code Quality Standards

**Code Style:**
```bash
# Format code with black
black . --line-length 100

# Sort imports with isort
isort . --profile black

# Lint with flake8
flake8 . --max-line-length 100 --ignore E203,W503
```

**Testing Requirements:**
- All new features must include tests
- Integration tests for system-level changes
- Mock external dependencies in unit tests
- Document test scenarios and expected outcomes

**Documentation Standards:**
- Docstrings for all public functions and classes
- README updates for user-facing changes
- Architecture documentation for system changes
- API documentation for new endpoints

### Git Workflow

**Branch Naming:**
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `test/description` - Test improvements

**Commit Messages:**
```
[Cursor] Component: Brief description

Detailed explanation of changes:
- What was changed
- Why it was changed
- Any breaking changes

Closes #issue-number
```

### Error Handling Patterns

**Cost Manager Errors:**
```python
try:
    cm = get_cost_manager()
    report = cm.start_operation("operation")
    # ... operation logic ...
except Exception as e:
    logger.error(f"Operation failed: {e}")
    # Cleanup and graceful degradation
finally:
    if 'report' in locals():
        cm.complete_operation("operation")
```

**LLM API Errors:**
```python
try:
    response = query_llm(prompt, provider="openai")
    if response is None:
        # Fallback strategy
        response = query_llm(prompt, provider="anthropic")
except Exception as e:
    logger.error(f"LLM query failed: {e}")
    return default_response
```

## 🔍 Debugging and Troubleshooting

### Common Development Issues

**1. Import Errors:**
```bash
# Ensure proper PYTHONPATH
export PYTHONPATH=$PWD:$PYTHONPATH

# Or use relative imports within package
from .shared.cost_manager import get_cost_manager
```

**2. Test Environment Issues:**
```bash
# Clean conda environment
conda env remove -n business-dev-automation
conda env create -f environment.yml

# Clean Docker environment
docker system prune -f
docker-compose -f docker-compose.integration.yml down -v
```

**3. Cost Tracking Not Working:**
```bash
# Check Prometheus server
curl http://localhost:8000/metrics

# Verify cost manager initialization
python -c "from shared.cost_manager import get_cost_manager; print(get_cost_manager().get_session_summary())"
```

### Debugging Tools

**Log Analysis:**
```bash
# View cost tracking logs
tail -f token_logs/session_$(date +%Y-%m-%d).json

# View system logs
tail -f logs/system.log
```

**Prometheus Metrics Debugging:**
```bash
# Check metrics endpoint
curl -s http://localhost:8000/metrics | grep llm_

# View specific metrics
curl -s http://localhost:8000/metrics | grep -A5 "llm_api_cost_total"
```

**Integration Test Debugging:**
```bash
# Run tests with verbose output
python test_integration.py --verbose

# Run specific failing test
pytest test_integration.py::TestClass::test_method -v -s
```

### Performance Profiling

**Cost Manager Performance:**
```python
import time
from shared.cost_manager import get_cost_manager

# Benchmark cost tracking overhead
start = time.time()
cm = get_cost_manager()
for i in range(1000):
    report = cm.start_operation(f"test_{i}")
    cm.track_api_call(f"test_{i}", api_response)
    cm.complete_operation(f"test_{i}")
print(f"1000 operations took: {time.time() - start:.2f}s")
```

## 🔧 IDE Setup Recommendations

### VS Code Configuration

**Extensions:**
- Python
- Pylance
- Python Docstring Generator
- GitLens
- Docker
- YAML

**Settings (.vscode/settings.json):**
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

### PyCharm Configuration

**Project Structure:**
- Mark `shared/` as Sources Root
- Mark `tests/` as Test Sources Root
- Configure Python interpreter to conda environment

**Run Configurations:**
- Integration Tests: `python test_integration.py`
- Cost Tracking Tests: `python test_cost_tracking.py`
- System Coordinator: `python system_coordinator.py --optimize-prompts --input "test"`

## 📈 Monitoring and Observability for Developers

### Development Monitoring

**Local Prometheus/Grafana Stack:**
```bash
# Start monitoring stack (if available)
docker-compose -f docker-compose.monitoring.yml up -d

# Access Grafana: http://localhost:3000
# Access Prometheus: http://localhost:9090
```

**Custom Metrics for Development:**
```python
from shared.cost_manager import get_cost_manager

# Add custom development metrics
cm = get_cost_manager()
cm.track_metagpt_event(
    'development_test',
    agent_type='developer',
    status='debugging',
    metadata={'feature': 'new_optimization'}
)
```

### Performance Monitoring

**Response Time Tracking:**
```python
import time
from shared.cost_manager import start_cost_tracking, complete_cost_tracking

# Track operation performance
start_cost_tracking("my_feature", {"version": "dev"})
start_time = time.time()

# ... your code here ...

duration = time.time() - start_time
report = complete_cost_tracking("my_feature")
print(f"Operation took {duration:.2f}s, cost ${report.total_cost:.6f}")
```

## 🚀 Advanced Development Topics

### Adding New LLM Providers

1. **Update Cost Calculation:**
```python
# In shared/cost_manager.py, add pricing logic
@staticmethod
def calculate_new_provider_cost(prompt_tokens, completion_tokens, model):
    # Add provider-specific pricing
    pass
```

2. **Update Integration:**
```python
# In archive/devin.cursorrules/tools/llm_api.py
def query_llm(prompt, provider="new_provider", ...):
    if provider == "new_provider":
        # Add provider implementation
        pass
```

3. **Add Tests:**
```python
# Add provider-specific tests to test_integration.py
def test_new_provider_cost_tracking(self):
    # Test new provider integration
    pass
```

### Extending Cost Tracking

**Custom Cost Reports:**
```python
from shared.cost_manager import CostReport, get_cost_manager

class CustomCostReport(CostReport):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_metrics = {}
    
    def add_custom_metric(self, name, value):
        self.custom_metrics[name] = value
```

**Custom Prometheus Metrics:**
```python
from prometheus_client import Counter, Histogram

# Add to cost_manager.py
custom_metric = Counter(
    'custom_operation_total',
    'Custom operation counter',
    ['operation_type']
)
```

### MetaGPT Integration Development

**Adding New Optimization Strategies:**
```python
# In prompt_optimizer_bot/optimize_prompt.py
def optimize_prompt(original_prompt, strategy="new_strategy"):
    if strategy == "new_strategy":
        # Implement new optimization approach
        pass
```

**Custom Agent Development:**
```python
# Create new agent in prompt_optimizer_bot/utils/
class CustomAgent:
    def __init__(self):
        self.cost_manager = get_cost_manager()
    
    def perform_action(self, action_name):
        self.cost_manager.track_metagpt_event(
            'agent_action',
            agent_type='CustomAgent',
            status=action_name
        )
```

## 📞 Getting Help

### Resources
- **Internal Documentation**: This guide and README.md
- **Architecture Diagrams**: See README.md system architecture section
- **API Reference**: See README.md API reference section
- **Test Examples**: Look at `test_integration.py` for patterns

### Escalation Path
1. Check this developer guide
2. Review existing tests for patterns
3. Check logs and run diagnostic tests
4. Ask team members for architecture questions
5. Create detailed issue with reproduction steps

### Contributing Guidelines
1. Follow the git workflow described above
2. Include comprehensive tests for all changes
3. Update documentation for user-facing changes
4. Run integration tests before submitting PRs
5. Follow code quality standards and review feedback

Welcome to the team! 🎉 