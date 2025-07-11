"""
System Coordinator for Business Development Automation
Orchestrates LeadGen, Outreach, and Perplexity bots in an integrated workflow
"""

import logging
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
from pathlib import Path


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemCoordinator:
    """
    Central coordinator for the business development automation system.
    Manages the workflow between lead generation, outreach, and market research.
    """
    
    def __init__(self, output_dir: str = "output", config_file: Optional[str] = None, 
                 credentials_path: Optional[str] = None, spreadsheet_id: Optional[str] = None):
        """
        Initialize the system coordinator.
        
        Args:
            output_dir: Directory for output files
            config_file: Optional configuration file path
            credentials_path: Path to Google Sheets service account credentials
            spreadsheet_id: Google Sheets spreadsheet ID
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = self._load_config(config_file) if config_file else {}
        
        # Google Sheets configuration
        self.credentials_path = credentials_path or "credentials/sheets-service-account.json"
        self.spreadsheet_id = spreadsheet_id
        
        # Initialize component coordinators (will be injected or mocked in tests)
        self.leadgen_coordinator = None
        self.outreach_coordinator = None
        self.perplexity_coordinator = None
        self.strategy_bot = None
        
        logger.info(f"SystemCoordinator initialized with output_dir: {self.output_dir}")
        if self.spreadsheet_id:
            logger.info(f"Google Sheets integration enabled: {self.spreadsheet_id}")
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config from {config_file}: {e}")
            return {}
    
    def run_full_pipeline(self, 
                         leadgen_config: Optional[Dict] = None,
                         outreach_config: Optional[Dict] = None,
                         research_config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Run the complete business development pipeline.
        
        Args:
            leadgen_config: Configuration for lead generation
            outreach_config: Configuration for outreach campaign  
            research_config: Configuration for market research
            
        Returns:
            Dictionary with results from all pipeline stages
        """
        logger.info("Starting full business development pipeline")
        
        results = {
            "pipeline_start": datetime.now().isoformat(),
            "success": False,
            "leadgen": {},
            "outreach": {},
            "perplexity": {},
            "errors": []
        }
        
        try:
            # Stage 1: Lead Generation
            logger.info("Stage 1: Running lead generation")
            leadgen_result = self._run_leadgen(leadgen_config or {})
            results["leadgen"] = leadgen_result
            
            # Stage 2: Outreach Campaign (if we have contacts)
            if leadgen_result.get("total_contacts", 0) > 0:
                logger.info("Stage 2: Running outreach campaign")
                outreach_result = self._run_outreach(outreach_config or {})
                results["outreach"] = outreach_result
            else:
                logger.warning("Stage 2: Skipping outreach - no contacts found")
                results["outreach"] = {
                    "emails_sent": 0,
                    "delivery_rate": 0.0,
                    "success": True,
                    "warning": "No contacts available for outreach"
                }
            
            # Stage 3: Market Research (independent of contacts)
            logger.info("Stage 3: Running market research")
            research_result = self._run_market_research(research_config or {})
            results["perplexity"] = research_result
            
            # Stage 4: Strategy Analysis (if requested and strategy config provided)
            if research_config and research_config.get("run_strategy_analysis", False):
                logger.info("Stage 4: Running strategy analysis")
                strategy_result = self._run_strategy_analysis(research_config.get("strategy_config", {}))
                results["strategy"] = strategy_result
            
            # Determine overall success
            results["success"] = (
                leadgen_result.get("success", False) and
                results["outreach"].get("success", False) and  
                research_result.get("success", False)
            )
            
            results["pipeline_end"] = datetime.now().isoformat()
            
            # Save pipeline results
            self._save_pipeline_results(results)
            
            logger.info(f"Pipeline completed with success: {results['success']}")
            return results
            
        except Exception as e:
            logger.error(f"Pipeline failed with error: {e}")
            results["errors"].append(str(e))
            results["success"] = False
            return results
    
    def _run_leadgen(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run lead generation stage"""
        try:
            # Try to import and use real LeadGenCoordinator
            try:
                from business_dev_automation.leadgen_bot import LeadGenCoordinator
                if self.leadgen_coordinator:
                    # Use injected coordinator (for testing)
                    return self.leadgen_coordinator.run_pipeline()
                else:
                    # Use real coordinator with Google Sheets integration
                    if self.spreadsheet_id and self.credentials_path:
                        coordinator = LeadGenCoordinator(self.credentials_path, self.spreadsheet_id)
                    else:
                        coordinator = LeadGenCoordinator()
                    return coordinator.run_pipeline()
            except ImportError:
                # Fallback for testing or development
                logger.warning("LeadGenCoordinator not available, using mock implementation")
                return self._mock_leadgen_result()
                
        except Exception as e:
            logger.error(f"Lead generation failed: {e}")
            return {"success": False, "error": str(e), "total_contacts": 0}
    
    def _run_outreach(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run outreach campaign stage"""
        try:
            # Try to import and use real OutreachCoordinator
            try:
                from business_dev_automation.outreach_bot import OutreachCoordinator
                if self.outreach_coordinator:
                    # Use injected coordinator (for testing)
                    return self.outreach_coordinator.run_outreach_campaign()
                else:
                    # Use real coordinator with Google Sheets integration
                    if self.spreadsheet_id and self.credentials_path:
                        coordinator = OutreachCoordinator(self.credentials_path, self.spreadsheet_id)
                    else:
                        coordinator = OutreachCoordinator()
                    return coordinator.run_outreach_campaign()
            except ImportError:
                # Fallback for testing or development
                logger.warning("OutreachCoordinator not available, using mock implementation")
                return self._mock_outreach_result()
                
        except Exception as e:
            logger.error(f"Outreach campaign failed: {e}")
            return {"success": False, "error": str(e), "emails_sent": 0}
    
    def _run_market_research(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run market research stage"""
        try:
            # Try to import and use real PerplexityCoordinator
            try:
                from business_dev_automation.perplexity_bot import PerplexityCoordinator
                if self.perplexity_coordinator:
                    # Use injected coordinator (for testing)
                    return self.perplexity_coordinator.generate_market_insights()
                else:
                    # Use real coordinator with Google Sheets integration
                    if self.spreadsheet_id and self.credentials_path:
                        coordinator = PerplexityCoordinator(self.credentials_path, self.spreadsheet_id)
                    else:
                        coordinator = PerplexityCoordinator()
                    return coordinator.generate_market_insights()
            except ImportError:
                # Fallback for testing or development
                logger.warning("PerplexityCoordinator not available, using mock implementation")
                return self._mock_perplexity_result()
                
        except Exception as e:
            logger.error(f"Market research failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _run_strategy_analysis(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run strategy analysis stage"""
        try:
            # Try to import and use real StrategyBot
            try:
                from business_dev_automation.strategy_bot import StrategyBot
                if self.strategy_bot:
                    # Use injected strategy bot (for testing)
                    company_name = config.get("company_name", "Target Company")
                    return self.strategy_bot.generate_strategy_analysis(company_name)
                else:
                    # Use real strategy bot with Google Sheets integration
                    if self.spreadsheet_id and self.credentials_path:
                        strategy_bot = StrategyBot(self.credentials_path, self.spreadsheet_id)
                    else:
                        strategy_bot = StrategyBot()
                    company_name = config.get("company_name", "Target Company")
                    return strategy_bot.generate_strategy_analysis(company_name)
            except ImportError:
                # Fallback for testing or development
                logger.warning("StrategyBot not available, using mock implementation")
                return self._mock_strategy_result()
                
        except Exception as e:
            logger.error(f"Strategy analysis failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _mock_leadgen_result(self) -> Dict[str, Any]:
        """Mock lead generation result for testing"""
        contacts_file = self.output_dir / "contacts_sg_my.csv"
        return {
            "total_contacts": 2,
            "contacts_file": str(contacts_file),
            "success": True,
            "sources_processed": ["SGTech", "MDEC"],
            "processing_time": "45.2s"
        }
    
    def _mock_outreach_result(self) -> Dict[str, Any]:
        """Mock outreach result for testing"""
        log_file = self.output_dir / "outreach_log.csv"
        return {
            "emails_sent": 2,
            "delivery_rate": 100.0,
            "log_file": str(log_file),
            "success": True,
            "campaign_type": "dev_tools_intro",
            "personalization_level": "high"
        }
    
    def _mock_perplexity_result(self) -> Dict[str, Any]:
        """Mock perplexity result for testing"""
        insights_file = self.output_dir / "market_insights.md"
        return {
            "insights_file": str(insights_file),
            "research_queries": 5,
            "success": True,
            "topics_covered": [
                "Singapore SME dev-tools adoption",
                "Malaysia software budget analysis",
                "Southeast Asia market trends"
            ]
        }
    
    def _mock_strategy_result(self) -> Dict[str, Any]:
        """Mock strategy result for testing"""
        return {
            "success": True,
            "company": "Target Company",
            "frameworks_applied": ["Porter's Five Forces", "Value Chain", "MECE Analysis"],
            "recommendations": [
                {"priority": "high", "text": "Focus on differentiation strategy"},
                {"priority": "medium", "text": "Optimize operational efficiency"}
            ],
            "executive_summary": "Strategic analysis completed with 3 frameworks applied and 2 key recommendations identified."
        }
    
    def _save_pipeline_results(self, results: Dict[str, Any]) -> None:
        """Save pipeline results to file"""
        results_file = self.output_dir / "pipeline_results.json"
        try:
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Pipeline results saved to {results_file}")
        except Exception as e:
            logger.error(f"Failed to save pipeline results: {e}")
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        try:
            results_file = self.output_dir / "pipeline_results.json"
            if results_file.exists():
                with open(results_file, 'r') as f:
                    return json.load(f)
            else:
                return {"status": "no_pipeline_runs", "message": "No pipeline executions found"}
        except Exception as e:
            logger.error(f"Failed to get pipeline status: {e}")
            return {"status": "error", "error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "components": {},
            "output_dir": str(self.output_dir),
            "output_dir_writable": os.access(self.output_dir, os.W_OK)
        }
        
        # Check component availability
        components = [
            ("leadgen_bot", "business_dev_automation.leadgen_bot"),
            ("outreach_bot", "business_dev_automation.outreach_bot"), 
            ("perplexity_bot", "business_dev_automation.perplexity_bot")
        ]
        
        for component_name, module_name in components:
            try:
                __import__(module_name)
                health_status["components"][component_name] = "available"
            except ImportError:
                health_status["components"][component_name] = "unavailable"
        
        # Check if any critical components are missing
        unavailable_components = [
            name for name, status in health_status["components"].items() 
            if status == "unavailable"
        ]
        
        if unavailable_components:
            health_status["status"] = "degraded"
            health_status["warnings"] = [
                f"Components unavailable: {', '.join(unavailable_components)}"
            ]
        
        return health_status


# Convenience classes for testing
class LeadGenCoordinator:
    """Placeholder for lead generation coordinator"""
    def run_pipeline(self):
        return {"success": True, "total_contacts": 0, "message": "Placeholder implementation"}


class OutreachCoordinator:
    """Placeholder for outreach coordinator"""
    def run_outreach_campaign(self):
        return {"success": True, "emails_sent": 0, "message": "Placeholder implementation"}


class PerplexityCoordinator:
    """Placeholder for perplexity coordinator"""
    def generate_market_insights(self):
        return {"success": True, "research_queries": 0, "message": "Placeholder implementation"}


# CLI interface for manual testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Business Development Automation System Coordinator")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--action", choices=["run", "status", "health"], default="run",
                       help="Action to perform")
    
    args = parser.parse_args()
    
    coordinator = SystemCoordinator(output_dir=args.output_dir, config_file=args.config)
    
    if args.action == "run":
        print("Running full business development pipeline...")
        results = coordinator.run_full_pipeline()
        print(json.dumps(results, indent=2))
    elif args.action == "status":
        print("Getting pipeline status...")
        status = coordinator.get_pipeline_status()
        print(json.dumps(status, indent=2))
    elif args.action == "health":
        print("Performing health check...")
        health = coordinator.health_check()
        print(json.dumps(health, indent=2)) 