# Business Development Automation System

**🤖 Automated lead generation, outreach, and market research for Southeast Asian SME markets**

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.9+ with pip
- Google Sheets account with service account credentials
- SendGrid API key for email outreach
- Perplexity API key for market research

### 2. Setup
```bash
# Clone and navigate
git clone https://github.com/company/bizdev-automation.git
cd bizdev-automation/business_dev_automation

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and Google Sheets ID

# Set up Google Sheets spreadsheet
python scripts/setup_google_sheets.py

# Run tests to verify setup
pytest test_sheets_client.py -v
```

### 3. Usage
```bash
# Run individual bots
python -m leadgen_bot --sources sgtech,mdec --limit 50
python -m outreach_bot --campaign intro_email --batch-size 10
python -m perplexity_bot --research-type market_trends

# Run complete pipeline
python system_coordinator.py --full-pipeline

# Generate strategy insights
python -m insights_bot --company "Tech Corp" --market-segment "SME software"
```

## 🏗️ Architecture Overview

### Core Components

**📊 Data Layer - Google Sheets**
- **Contacts**: Lead information from SGTech, MDEC, LinkedIn
- **Outreach_Log**: Email campaign tracking and metrics
- **Market_Insights**: Research findings and trend analysis
- **Strategy_Reports**: McKinsey-style business analysis

**🤖 Bot Ecosystem**
- **LeadGen-Bot**: Automated scraping with compliance controls
- **Outreach-Bot**: Personalized email campaigns with LLM integration
- **PerplexityMCP-Bot**: Market research with Southeast Asian focus
- **Insights-Bot**: Strategic analysis using consulting frameworks
- **Strategy-Bot**: McKinsey-style presentations and recommendations

**🔧 Infrastructure**
- **System Coordinator**: Orchestrates multi-bot workflows
- **Rate Limiting**: Google Sheets API compliance (90 req/100s)
- **Error Handling**: 3-retry mechanism with exponential backoff
- **Monitoring**: Health checks and performance metrics

### Data Flow
```
SGTech/MDEC → LeadGen-Bot → Google Sheets (Contacts)
                                  ↓
Google Sheets (Contacts) → Outreach-Bot → Email Delivery
                                  ↓
                       Outreach_Log (Google Sheets)

Market Research → PerplexityMCP-Bot → Market_Insights (Google Sheets)
                                              ↓
Strategy Analysis → Insights-Bot → Strategy_Reports (Google Sheets)
```

## 📈 Features

### Lead Generation
- **SGTech Directory**: Singapore technology companies
- **MDEC Directory**: Malaysia digital economy companies  
- **LinkedIn Groups**: Professional network mining
- **Deduplication**: Smart contact consolidation
- **Compliance**: GDPR/PDPA data protection

### Outreach Automation
- **LLM Personalization**: GPT-4 powered message generation
- **A/B Testing**: Campaign optimization
- **Delivery Tracking**: SendGrid/SMTP integration
- **Success Metrics**: Open rates, response tracking

### Market Research
- **Regional Focus**: Malaysia/Singapore SME markets
- **Trend Analysis**: Dev-tools adoption patterns
- **Budget Insights**: Software spending analysis
- **Competitive Intelligence**: Market positioning

### Strategic Analysis
- **McKinsey Frameworks**: Porter's 5 Forces, Value Chain, MECE
- **PowerPoint Generation**: Branded slide decks
- **Executive Summaries**: C-level ready insights
- **Cost Optimization**: Token usage tracking

## 🚀 Deployment

### Development
```bash
# Run individual components
python -m pytest  # Run all tests
python system_coordinator.py --mock-mode  # Test pipeline

# Performance testing
python -m locust -f locustfile.py --host=http://localhost:8000
```

### Production
```bash
# One-command deployment
curl -fsSL https://raw.githubusercontent.com/company/bizdev-automation/main/deploy.sh | bash

# Manual deployment
docker compose -f docker-compose.prod.yml up -d
```

See [README-deploy.md](README-deploy.md) for detailed deployment instructions.

## 📊 Performance Specifications

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Throughput (250 users) | >20 req/sec | 22.1 req/sec | ✅ |
| Latency (95th percentile) | <5s | 4.8s | ✅ |
| Error Rate (stress test) | <10% | 8.2% | ✅ |
| Integration Tests | 4/4 passing | 4/4 passing | ✅ |

## 🔒 Security & Compliance

- **GDPR/PDPA Compliance**: Data anonymization and consent management
- **Rate Limiting**: Google Sheets API compliance (90 req/100s)
- **Error Handling**: 3-retry mechanism with exponential backoff
- **Authentication**: Service account credentials for Google Sheets
- **Monitoring**: Health checks and security scanning

See [compliance/security_checklist.md](compliance/security_checklist.md) for full details.

## 📚 Documentation

- **[Deployment Guide](README-deploy.md)**: Production deployment instructions
- **[Performance Report](docs/performance_report.md)**: Load testing results
- **[Security Checklist](compliance/security_checklist.md)**: Compliance framework
- **[Migration Plan](MIGRATION_PLAN.md)**: MongoDB to Google Sheets migration
- **[Changelog](CHANGELOG.md)**: Version history and updates

## 🛠️ Development

### Project Structure
```
business_dev_automation/
├── leadgen_bot/           # Lead generation components
├── outreach_bot/          # Email campaign automation  
├── perplexity_bot/        # Market research engine
├── insights_bot/          # Strategic analysis tools
├── strategy_bot/          # McKinsey-style frameworks
├── shared/                # Common utilities
│   └── sheets_client.py   # Google Sheets integration
├── system_coordinator.py  # Pipeline orchestration
└── tests/                 # Test suites
```

### Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Testing
```bash
# Unit tests
pytest test_sheets_client.py -v

# Integration tests  
pytest test_integration_int.py -v

# Performance tests
python -m locust -f locustfile.py --headless --users=100 --spawn-rate=10 --run-time=5m
```

## 📞 Support

- **Documentation**: [GitHub Wiki](https://github.com/company/bizdev-automation/wiki)
- **Issues**: [GitHub Issues](https://github.com/company/bizdev-automation/issues)
- **Email**: devops@company.com
- **Slack**: #bizdev-automation

## 📄 License

This project is proprietary software owned by [Company Name]. All rights reserved.

---

**🎯 Ready to automate your business development pipeline?** 

Start with the [Quick Start](#-quick-start) guide above or jump to [Production Deployment](README-deploy.md) for full setup. 