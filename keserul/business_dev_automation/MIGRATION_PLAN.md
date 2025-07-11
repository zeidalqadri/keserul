# Migration & Deployment Plan: MongoDB → Google Sheets + Strategy-Bot

## Executive Summary

This document outlines the migration strategy for transitioning the Business Development Automation System from MongoDB to Google Sheets as the primary data store, while adding a new Strategy-Bot for McKinsey-style analysis.

## Current Architecture Assessment

### Existing Components
- **LeadGen-Bot**: Scrapes SGTech, MDEC, LinkedIn → writes to MongoDB
- **Outreach-Bot**: Reads contacts from MongoDB → sends emails → logs to MongoDB  
- **PerplexityMCP-Bot**: Market research → writes insights to MongoDB
- **Insights-Bot**: McKinsey-style analysis and deck generation

### Dependencies to Migrate
- `shared/database.py`: MongoDB connection and operations
- `system_coordinator.py`: Orchestration with MongoDB queries
- `docker-compose.prod.yml`: MongoDB service definition
- All bot modules: MongoDB read/write operations

## Migration Strategy

### Phase 1: Google Sheets Infrastructure (Week 1)
**Goal**: Establish Google Sheets API integration and schema

#### 1.1 Google Sheets API Setup
- Create Google Cloud Project with Sheets API enabled
- Generate service account credentials (JSON key file)
- Install `gspread` and `google-auth` libraries
- Implement authentication and connection management

#### 1.2 Schema Design
Create 4 main worksheets:
- **Contacts**: name, role, company, email, linkedin_url, source, scraped_date, status
- **Outreach_Log**: contact_id, message_type, sent_date, delivery_status, response_status
- **Market_Insights**: query, research_date, findings, source, region, industry
- **Strategy_Reports**: company, analysis_date, mckinsey_framework, recommendations, deck_path

#### 1.3 Rate Limiting & Concurrency
- Implement exponential backoff for API calls
- Create connection pool with max 10 concurrent requests
- Add caching layer using Redis for frequently accessed data

### Phase 2: Bot Migration (Week 2)
**Goal**: Update all bots to use Google Sheets instead of MongoDB

#### 2.1 Shared Google Sheets Module
```python
# shared/sheets_client.py
class SheetsClient:
    def __init__(self, credentials_path, spreadsheet_id):
        # Initialize with service account
    
    def write_contacts(self, contacts_data):
        # Batch write to Contacts worksheet
    
    def read_contacts(self, filters=None):
        # Read with optional filtering
    
    def update_outreach_status(self, contact_id, status):
        # Update specific row in Outreach_Log
```

#### 2.2 Bot Updates
- **LeadGen-Bot**: Replace MongoDB writes with `sheets_client.write_contacts()`
- **Outreach-Bot**: Replace MongoDB reads/writes with Sheets operations
- **PerplexityMCP-Bot**: Write insights to Market_Insights worksheet

### Phase 3: Strategy-Bot Implementation (Week 3)
**Goal**: Create new Strategy-Bot leveraging insights_bot framework

#### 3.1 Strategy-Bot Architecture
```
strategy_bot/
├── __init__.py
├── strategy_analyzer.py      # Core McKinsey framework analysis
├── sheets_integration.py     # Google Sheets data connector
├── report_generator.py       # Strategy report creation
└── mckinsey_templates.py     # Framework templates (MECE, Issue Tree, etc.)
```

#### 3.2 McKinsey Framework Integration
- Leverage existing `insights_bot/prompts/base_prompt.md`
- Add McKinsey-specific templates: MECE, Issue Trees, Hypothesis-driven analysis
- Integrate with `insights_bot/utils/conversation_orchestrator.py`

#### 3.3 Data Flow
1. Read market insights from Google Sheets
2. Apply McKinsey frameworks via LLM analysis
3. Generate strategy recommendations
4. Write reports back to Strategy_Reports worksheet
5. Optional: Generate PowerPoint decks using existing DeckAssembler

### Phase 4: System Integration (Week 4)
**Goal**: Update orchestration and ensure end-to-end functionality

#### 4.1 System Coordinator Updates
```python
# system_coordinator.py changes
class SystemCoordinator:
    def __init__(self):
        self.sheets_client = SheetsClient()
        self.strategy_bot = StrategyBot()
    
    def run_full_pipeline(self):
        # LeadGen → Outreach → Market Research → Strategy Analysis
```

#### 4.2 Docker Compose Updates
```yaml
# Remove MongoDB service
# Add Google Sheets service account volume
services:
  leadgen_worker:
    volumes:
      - ./credentials/sheets-service-account.json:/app/credentials/
  
  strategy_worker:
    build: ./strategy_bot
    volumes:
      - ./credentials/sheets-service-account.json:/app/credentials/
```

## Technical Specifications

### Google Sheets API Limits & Mitigation
- **Rate Limit**: 100 requests/100 seconds per user
- **Mitigation**: 
  - Batch operations (up to 1000 rows per request)
  - Exponential backoff with jitter
  - Connection pooling and retry logic
  - Local caching for read-heavy operations

### Authentication Strategy
- **Service Account**: Recommended for production automation
- **Scope**: `https://www.googleapis.com/auth/spreadsheets`
- **Security**: Store credentials as Docker secrets, not environment variables

### Data Migration Scripts
```python
# scripts/migrate_mongodb_to_sheets.py
def migrate_contacts():
    # Read from MongoDB
    # Transform to Sheets schema
    # Batch upload to Google Sheets
    
def migrate_outreach_logs():
    # Similar pattern for outreach data
```

## Risk Assessment & Mitigation

### High-Risk Areas
1. **Data Loss During Migration**
   - Mitigation: Full MongoDB backup before migration
   - Verification: Row count and hash validation post-migration

2. **Google Sheets API Quota Exceeded**
   - Mitigation: Implement circuit breaker pattern
   - Fallback: Queue operations in Redis when API unavailable

3. **Concurrent Write Conflicts**
   - Mitigation: Row-level locking using Redis distributed locks
   - Pattern: Last-writer-wins with conflict detection

### Medium-Risk Areas
1. **Authentication Token Expiry**
   - Mitigation: Automatic token refresh with service accounts
   
2. **Schema Evolution**
   - Mitigation: Versioned worksheet templates and migration scripts

## Testing Strategy

### Unit Tests
- Google Sheets API client with mocked responses
- Strategy-Bot McKinsey framework logic
- Data transformation and validation

### Integration Tests  
- End-to-end pipeline: LeadGen → Outreach → Strategy
- Google Sheets read/write operations with test spreadsheet
- Error handling and retry mechanisms

### Performance Tests
- Load testing with 1000+ concurrent operations
- API rate limit testing and backoff validation
- Memory usage optimization for large datasets

## Deployment Timeline

### Week 1: Infrastructure (Jan 13-19)
- [ ] Google Cloud Project setup and API enablement
- [ ] Service account creation and credential management
- [ ] Google Sheets schema design and creation
- [ ] Basic API client implementation with rate limiting

### Week 2: Bot Migration (Jan 20-26)
- [ ] Shared sheets client module
- [ ] LeadGen-Bot Google Sheets integration
- [ ] Outreach-Bot migration
- [ ] PerplexityMCP-Bot migration
- [ ] Data migration scripts

### Week 3: Strategy-Bot (Jan 27-Feb 2)
- [ ] Strategy-Bot module creation
- [ ] McKinsey framework integration
- [ ] Google Sheets data connectors
- [ ] Report generation and deck assembly

### Week 4: Integration & Testing (Feb 3-9)
- [ ] System coordinator updates
- [ ] Docker compose production configuration
- [ ] Comprehensive testing suite
- [ ] Documentation and deployment guides
- [ ] Production deployment

## Success Metrics

### Functional Requirements
- [ ] All existing bot functionality preserved
- [ ] Strategy-Bot generates McKinsey-style reports
- [ ] End-to-end pipeline completes without errors
- [ ] Data consistency between old and new systems

### Performance Requirements
- [ ] API operations complete within 5 seconds (95th percentile)
- [ ] System handles 100+ concurrent bot operations
- [ ] Zero data loss during migration
- [ ] <2% increase in operational costs

### Security Requirements
- [ ] Service account authentication implemented
- [ ] Credentials securely stored and rotated
- [ ] GDPR/PDPA compliance maintained
- [ ] Audit logging for all data operations

## Rollback Plan

### Emergency Rollback (< 1 hour)
1. Revert docker-compose.prod.yml to MongoDB version
2. Restart all services with previous container images
3. Verify MongoDB data integrity
4. Resume operations with original architecture

### Partial Rollback (Bot-by-Bot)
1. Individual bot rollback to MongoDB operations
2. Gradual migration completion over extended timeline
3. Parallel operation of both systems during transition

## Post-Migration Optimization

### Performance Enhancements
- Implement Google Sheets caching layer
- Optimize batch operations for large datasets
- Add read replicas using Google Sheets backup copies

### Feature Additions
- Real-time collaboration features using Sheets comments
- Advanced filtering and search capabilities
- Integration with Google Data Studio for analytics

## Conclusion

This migration plan provides a structured approach to transitioning from MongoDB to Google Sheets while adding valuable McKinsey-style analysis capabilities. The phased approach minimizes risk while ensuring business continuity throughout the transition. 