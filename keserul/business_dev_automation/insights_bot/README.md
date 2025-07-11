# McKinsey-Insights Bot

A powerful tool for generating McKinsey-style market analysis and strategic recommendations with automated PowerPoint deck creation.

## Overview

The McKinsey-Insights Bot is designed to streamline the process of market research, strategic analysis, and presentation creation. It uses advanced LLMs to guide users through a structured consulting methodology, gathering information and generating insights at each phase.

Key features:
- Phased conversation flow following McKinsey consulting methodology
- Intelligent model selection based on task complexity
- Cost tracking and budget management
- Automatic PowerPoint deck generation
- Chart and visualization specifications

## Architecture

The system consists of the following components:

1. **ConversationOrchestrator**: Manages the conversation flow using a finite-state machine
2. **PromptTemplateManager**: Handles prompt templates and variable injection
3. **LLMClient**: Manages LLM API calls with cost tracking and model selection
4. **DeckAssembler**: Generates PowerPoint presentations from conversation data

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/business-dev-automation.git
cd business-dev-automation

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from insights_bot.utils.conversation_orchestrator import ConversationOrchestrator
from insights_bot.utils.prompt_manager import PromptTemplateManager
from insights_bot.utils.llm_client import LLMClient
from insights_bot.utils.deck_assembler import DeckAssembler

# Initialize components
prompt_manager = PromptTemplateManager()
llm_client = LLMClient()
orchestrator = ConversationOrchestrator(prompt_manager, llm_client)
deck_assembler = DeckAssembler()

# Start a new conversation
variables = {
    "company_name": "Acme Corp",
    "market_segment": "Software",
    "region": "Asia Pacific",
    "time_period": "2023-2025"
}
context = orchestrator.start_conversation(variables)

# Process user messages
response, state = orchestrator.process_user_message(context, "Tell me about the software market in Asia Pacific")
print(f"Response: {response}")
print(f"Current state: {state}")

# Continue to the next phase
response, state = orchestrator.process_user_message(context, "continue")
print(f"Response: {response}")
print(f"Current state: {state}")

# ... continue through all phases ...

# Generate a presentation
presentation = deck_assembler.create_presentation(context.to_dict())
output_path = deck_assembler.save_presentation(presentation, "acme_corp_analysis.pptx")
print(f"Presentation saved to: {output_path}")
```

### Command Line Interface

```bash
# Start a new conversation
python -m insights_bot.cli --company "Acme Corp" --market "Software" --region "Asia Pacific" --period "2023-2025"

# This will start an interactive session where you can chat with the bot
# Type 'continue' to move to the next phase
# Type 'finalize' in Phase 6 to finalize the analysis
# Type 'complete' in the Finalization phase to generate the deck
```

## Conversation Phases

The bot guides users through the following phases:

1. **Initial Data Collection**: Gathering information about the company, market, and objectives
2. **Executive Summary & Key Insights**: High-level overview and key findings
3. **Market Overview & Competitive Landscape**: Market size, growth, trends, and competitors
4. **Customer Analysis & Company Position**: Customer segments, needs, and company positioning
5. **Strategic Options & Recommendations**: Strategic alternatives and recommended approach
6. **Implementation Plan & Expected Outcomes**: Action steps and projected results

## Cost Management

The bot includes built-in cost management features:

- **Budget Ceiling**: Set maximum spending limits in `cost_budget.yml`
- **Model Selection**: Automatically selects the appropriate model based on task complexity
- **Cost Tracking**: Monitors token usage and costs by phase
- **Usage Reports**: Generates detailed reports of token usage and costs

### Cost Guidelines

| Phase | Typical Token Usage | Estimated Cost (USD) |
|-------|---------------------|----------------------|
| Phase 1 | 1,000-2,000 | $0.02-$0.04 |
| Phase 2 | 3,000-5,000 | $0.06-$0.10 |
| Phase 3 | 4,000-6,000 | $0.08-$0.12 |
| Phase 4 | 3,000-5,000 | $0.06-$0.10 |
| Phase 5 | 4,000-7,000 | $0.08-$0.14 |
| Phase 6 | 3,000-5,000 | $0.06-$0.10 |
| Finalization | 2,000-3,000 | $0.04-$0.06 |
| **Total** | **20,000-33,000** | **$0.40-$0.66** |

*Note: Costs are estimated based on GPT-4 API pricing. Actual costs may vary depending on model selection and conversation complexity.*

## Chart Generation

The bot can generate chart specifications in the following format:

```
## Chart Specification
For the Market Share chart:
**Chart Type**: Pie
**Data Series**:
- Company A: [30, 25, 20]
- Company B: [20, 25, 30]
- Company C: [50, 50, 50]
**X-Axis**: Years
**Y-Axis**: Market Share (%)
**Colors**: Primary: #0066CC, Secondary: #FF9900
**Labels**: True
**Legend**: True
**Notes**: Data from industry reports

This chart shows the market share of the top three companies over time.
```

These specifications are automatically extracted and used to generate charts in the PowerPoint presentation.

## Customization

### Prompt Templates

You can customize the prompt templates in the `prompts` directory:

- `base_prompt.md`: The base system prompt
- `phases.md`: Phase-specific prompts
- `finalization.md`: Finalization prompt

### PowerPoint Template

To use a custom PowerPoint template:

```python
deck_assembler = DeckAssembler(template_path="path/to/template.pptx")
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest insights_bot/tests/test_conversation_orchestrator.py

# Run with coverage
pytest --cov=insights_bot
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 