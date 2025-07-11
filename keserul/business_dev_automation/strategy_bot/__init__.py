"""Strategy Bot Package - McKinsey Framework Analysis"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

# Import Google Sheets client
try:
    from business_dev_automation.shared.sheets_client import SheetsClient
except ImportError:
    SheetsClient = None

# Import insights_bot components
try:
    from business_dev_automation.insights_bot.utils.conversation_orchestrator import ConversationOrchestrator
    from business_dev_automation.insights_bot.utils.prompt_manager import PromptTemplateManager
    from business_dev_automation.insights_bot.utils.llm_client import LLMClient
    from business_dev_automation.insights_bot.utils.deck_assembler import DeckAssembler
except ImportError:
    ConversationOrchestrator = None
    PromptTemplateManager = None
    LLMClient = None
    DeckAssembler = None

logger = logging.getLogger(__name__)


class StrategyBot:
    """Strategy analysis bot using McKinsey frameworks and Google Sheets integration"""
    
    def __init__(self, credentials_path: str = None, spreadsheet_id: str = None):
        """
        Initialize Strategy bot.
        
        Args:
            credentials_path: Path to Google Sheets service account credentials
            spreadsheet_id: Google Sheets spreadsheet ID
        """
        self.credentials_path = credentials_path or "credentials/sheets-service-account.json"
        self.spreadsheet_id = spreadsheet_id
        self.sheets_client = None
        
        # Initialize Google Sheets client if available
        if (SheetsClient and 
            isinstance(self.spreadsheet_id, str) and 
            isinstance(self.credentials_path, str)):
            try:
                self.sheets_client = SheetsClient(self.credentials_path, self.spreadsheet_id)
                logger.info("Strategy Bot connected to Google Sheets")
            except Exception as e:
                logger.warning(f"Could not connect to Google Sheets: {e}")
        
        # Initialize insights_bot components if available
        self.prompt_manager = None
        self.llm_client = None
        self.orchestrator = None
        self.deck_assembler = None
        
        if all([PromptTemplateManager, LLMClient, ConversationOrchestrator, DeckAssembler]):
            try:
                self.prompt_manager = PromptTemplateManager(None)
                self.llm_client = LLMClient()
                self.orchestrator = ConversationOrchestrator(self.prompt_manager, self.llm_client)
                self.deck_assembler = DeckAssembler()
                logger.info("Strategy Bot integrated with insights_bot components")
            except Exception as e:
                logger.warning(f"Could not initialize insights_bot components: {e}")
        
        # Initialize McKinsey frameworks
        self.mckinsey_frameworks = McKinseyFrameworks()
    
    def generate_strategy_analysis(self, company_name: str, market_segment: str = "Software Development") -> Dict[str, Any]:
        """
        Generate comprehensive strategy analysis using McKinsey frameworks.
        
        Args:
            company_name: Name of company to analyze
            market_segment: Market segment to focus on
            
        Returns:
            Dict with analysis results
        """
        results = {
            "success": False,
            "company": company_name,
            "analysis_date": datetime.now().isoformat(),
            "frameworks_applied": [],
            "recommendations": [],
            "deck_path": None,
            "executive_summary": "",
            "errors": []
        }
        
        try:
            logger.info(f"Starting strategy analysis for {company_name} in {market_segment}")
            
            # Gather market insights from Google Sheets
            market_data = self._gather_market_insights(market_segment)
            
            # Apply McKinsey frameworks
            frameworks_results = self._apply_mckinsey_frameworks(
                company_name, market_segment, market_data
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(frameworks_results)
            
            # Create executive summary
            executive_summary = self._create_executive_summary(
                company_name, frameworks_results, recommendations
            )
            
            # Generate PowerPoint deck if possible
            deck_path = self._generate_strategy_deck(
                company_name, frameworks_results, recommendations
            )
            
            # Store strategy report in Google Sheets
            strategy_report = {
                "id": str(uuid.uuid4()),
                "company": company_name,
                "analysis_date": datetime.now().isoformat(),
                "mckinsey_framework": ", ".join([f["name"] for f in frameworks_results]),
                "recommendations": "\n".join([r["text"] for r in recommendations]),
                "deck_path": deck_path or "",
                "executive_summary": executive_summary,
                "created_at": datetime.now().isoformat()
            }
            
            if self.sheets_client:
                success = self.sheets_client.write_strategy_reports([strategy_report])
                if success:
                    logger.info("Successfully stored strategy report in Google Sheets")
                else:
                    logger.error("Failed to store strategy report in Google Sheets")
                    results["errors"].append("Google Sheets storage failed")
            
            # Update results
            results.update({
                "success": True,
                "frameworks_applied": [f["name"] for f in frameworks_results],
                "recommendations": recommendations,
                "deck_path": deck_path,
                "executive_summary": executive_summary
            })
            
            logger.info(f"Strategy analysis completed for {company_name}")
            return results
            
        except Exception as e:
            logger.error(f"Strategy analysis failed: {e}")
            results["errors"].append(str(e))
            return results
    
    def _gather_market_insights(self, market_segment: str) -> List[Dict[str, Any]]:
        """Gather market insights from Google Sheets."""
        if not self.sheets_client:
            logger.warning("Google Sheets not available, using mock market data")
            return self._get_mock_market_data(market_segment)
        
        try:
            insights = self.sheets_client.read_market_insights({
                "industry": market_segment
            })
            logger.info(f"Retrieved {len(insights)} market insights from Google Sheets")
            return insights
        except Exception as e:
            logger.error(f"Failed to read market insights: {e}")
            return self._get_mock_market_data(market_segment)
    
    def _get_mock_market_data(self, market_segment: str) -> List[Dict[str, Any]]:
        """Generate mock market data for testing."""
        return [
            {
                "query": "Southeast Asia SME software development trends",
                "findings": "Strong growth in cloud adoption and DevOps automation",
                "summary": "Market showing 40% growth in dev-tools adoption",
                "region": "Singapore, Malaysia"
            }
        ]
    
    def _apply_mckinsey_frameworks(self, company: str, segment: str, market_data: List[Dict]) -> List[Dict[str, Any]]:
        """Apply McKinsey frameworks to the analysis."""
        results = []
        
        # Porter's Five Forces
        five_forces = self.mckinsey_frameworks.analyze_five_forces(company, segment, market_data)
        results.append(five_forces)
        
        # Value Chain Analysis
        value_chain = self.mckinsey_frameworks.analyze_value_chain(company, segment)
        results.append(value_chain)
        
        # MECE Problem Structuring
        mece_analysis = self.mckinsey_frameworks.mece_problem_structure(company, segment, market_data)
        results.append(mece_analysis)
        
        return results
    
    def _generate_recommendations(self, frameworks_results: List[Dict]) -> List[Dict[str, Any]]:
        """Generate strategic recommendations based on framework analysis."""
        recommendations = []
        
        for framework in frameworks_results:
            if framework["name"] == "Porter's Five Forces":
                recommendations.append({
                    "priority": "high",
                    "text": "Focus on differentiation to reduce competitive rivalry",
                    "framework": "Porter's Five Forces",
                    "rationale": "Analysis shows high competitive intensity in the market"
                })
            
            elif framework["name"] == "Value Chain":
                recommendations.append({
                    "priority": "medium", 
                    "text": "Optimize technology infrastructure to reduce costs",
                    "framework": "Value Chain",
                    "rationale": "Value chain analysis identifies efficiency opportunities"
                })
            
            elif framework["name"] == "MECE Analysis":
                recommendations.append({
                    "priority": "high",
                    "text": "Expand into emerging Southeast Asian markets",
                    "framework": "MECE Analysis", 
                    "rationale": "Market structure analysis shows growth opportunities"
                })
        
        return recommendations
    
    def _create_executive_summary(self, company: str, frameworks: List[Dict], recommendations: List[Dict]) -> str:
        """Create executive summary of the analysis."""
        high_priority_recs = [r for r in recommendations if r["priority"] == "high"]
        
        summary = f"""Strategic Analysis Summary for {company}

Key Findings:
• Applied {len(frameworks)} McKinsey frameworks to assess market position
• Identified {len(high_priority_recs)} high-priority strategic opportunities
• Market analysis indicates strong growth potential in Southeast Asian SME segment

Top Recommendations:
{chr(10).join(['• ' + r['text'] for r in high_priority_recs[:3]])}

Next Steps:
• Develop detailed implementation roadmap
• Allocate resources for top-priority initiatives
• Establish success metrics and monitoring framework"""
        
        return summary
    
    def _generate_strategy_deck(self, company: str, frameworks: List[Dict], recommendations: List[Dict]) -> Optional[str]:
        """Generate PowerPoint strategy deck using insights_bot components."""
        if not self.deck_assembler:
            logger.warning("DeckAssembler not available, skipping deck generation")
            return None
        
        try:
            # Mock conversation context for deck generation
            from business_dev_automation.insights_bot.utils.conversation_orchestrator import ConversationContext
            
            context = ConversationContext()
            context.company_name = company
            context.market_segment = "Software Development"
            context.region = "Southeast Asia"
            
            # Add framework results to context
            for framework in frameworks:
                context.add_message("assistant", f"Framework Analysis: {framework['analysis']}")
            
            # Generate deck
            deck_path = f"output/{company}_strategy_analysis_{datetime.now().strftime('%Y%m%d')}.pptx"
            self.deck_assembler.create_deck(context, deck_path)
            
            logger.info(f"Generated strategy deck: {deck_path}")
            return deck_path
            
        except Exception as e:
            logger.error(f"Failed to generate strategy deck: {e}")
            return None


class McKinseyFrameworks:
    """Implementation of core McKinsey strategic analysis frameworks"""
    
    def analyze_five_forces(self, company: str, segment: str, market_data: List[Dict]) -> Dict[str, Any]:
        """Apply Porter's Five Forces framework."""
        analysis = f"""Porter's Five Forces Analysis for {company} in {segment}:

1. Competitive Rivalry: HIGH
   - Numerous established players in development tools market
   - Low switching costs for customers
   - Rapid technological change driving competition

2. Supplier Power: MEDIUM
   - Cloud infrastructure providers have significant power
   - Multiple technology stack options available
   - Growing importance of AI/ML capabilities

3. Buyer Power: HIGH
   - SME customers highly price-sensitive
   - Low switching costs between tools
   - Increasing sophistication of buyer requirements

4. Threat of Substitutes: HIGH
   - Open-source alternatives widely available
   - In-house development capabilities growing
   - Platform consolidation reducing tool count

5. Barriers to Entry: MEDIUM
   - High technical expertise required
   - Significant R&D investment needed
   - Network effects and ecosystem lock-in possible"""
        
        return {
            "name": "Porter's Five Forces",
            "analysis": analysis,
            "key_insights": [
                "High competitive intensity requires differentiation strategy",
                "Customer power demands value-focused positioning",
                "Barriers to entry suggest focus on specialized niches"
            ]
        }
    
    def analyze_value_chain(self, company: str, segment: str) -> Dict[str, Any]:
        """Apply Value Chain analysis framework."""
        analysis = f"""Value Chain Analysis for {company}:

Primary Activities:
• Inbound Logistics: Technology acquisition and integration
• Operations: Software development and platform management
• Outbound Logistics: Digital distribution and deployment
• Marketing & Sales: Digital marketing and direct sales
• Service: Customer support and success management

Support Activities:
• Firm Infrastructure: Cloud-native architecture and DevOps
• Human Resource Management: Technical talent acquisition
• Technology Development: R&D and innovation capabilities
• Procurement: Third-party integrations and partnerships

Cost Optimization Opportunities:
• Automate customer onboarding and support
• Leverage open-source components strategically
• Implement efficient CI/CD pipelines
• Optimize cloud infrastructure costs"""
        
        return {
            "name": "Value Chain",
            "analysis": analysis,
            "key_insights": [
                "Technology development is primary value driver",
                "Automation opportunities in support functions",
                "Cloud optimization can reduce operational costs"
            ]
        }
    
    def mece_problem_structure(self, company: str, segment: str, market_data: List[Dict]) -> Dict[str, Any]:
        """Apply MECE (Mutually Exclusive, Collectively Exhaustive) problem structuring."""
        analysis = f"""MECE Problem Structure for {company} Market Strategy:

Market Dimensions (Mutually Exclusive):
1. Geographic Markets
   - Singapore: Mature, high-value, strong compliance needs
   - Malaysia: Emerging, price-sensitive, growth-focused
   - Thailand/Indonesia: Future expansion opportunities

2. Customer Segments
   - Early-stage startups: Price-sensitive, agility-focused
   - Growth-stage SMEs: Scalability and integration needs
   - Enterprise subsidiaries: Compliance and security requirements

3. Product Categories
   - Core development tools: IDEs, frameworks, libraries
   - DevOps platforms: CI/CD, monitoring, deployment
   - Collaboration tools: Project management, communication

Strategic Options (Collectively Exhaustive):
A. Geographic Expansion: Focus on underserved markets
B. Vertical Integration: Build comprehensive platform
C. Horizontal Expansion: Add adjacent product categories
D. Partnership Strategy: Integrate with existing ecosystems"""
        
        return {
            "name": "MECE Analysis",
            "analysis": analysis,
            "key_insights": [
                "Clear market segmentation enables targeted strategies", 
                "Multiple expansion vectors available for growth",
                "Partnership approach may accelerate market entry"
            ]
        }


__all__ = ["StrategyBot"] 