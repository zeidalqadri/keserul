"""
Tests for the PromptTemplateManager class.
"""

import os
import unittest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from business_dev_automation.insights_bot.utils.prompt_manager import PromptTemplateManager


class TestPromptTemplateManager(unittest.TestCase):
    """Test cases for the PromptTemplateManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = PromptTemplateManager()
        
        # Test variables for template rendering
        self.test_variables = {
            "company_name": "TechCorp",
            "market_segment": "Cloud Computing",
            "region": "Southeast Asia",
            "time_period": "2023-2025",
            "primary_color": "#0066CC",
            "secondary_color": "#FF9900",
            "deck_title": "Cloud Market Analysis",
            "ceo_question": "How can we increase our market share?",
            "additional_data_sources": ["IDC Reports", "Gartner Analysis"]
        }
    
    def test_get_template(self):
        """Test getting a template by name."""
        template = self.manager.get_template("base_prompt.md")
        self.assertIsNotNone(template)
    
    def test_render_base_prompt(self):
        """Test rendering the base prompt template."""
        rendered = self.manager.render_base_prompt(self.test_variables)
        
        # Check that variables were properly inserted
        self.assertIn("TechCorp", rendered)
        self.assertIn("Cloud Computing", rendered)
        self.assertIn("Southeast Asia", rendered)
        self.assertIn("2023-2025", rendered)
        self.assertIn("#0066CC", rendered)
        self.assertIn("#FF9900", rendered)
        self.assertIn("Cloud Market Analysis", rendered)
        self.assertIn("How can we increase our market share?", rendered)
        self.assertIn("IDC Reports", rendered)
        self.assertIn("Gartner Analysis", rendered)
    
    def test_render_phase(self):
        """Test rendering a phase template."""
        rendered = self.manager.render_phase(2, self.test_variables)
        
        # Check that variables were properly inserted
        self.assertIn("TechCorp", rendered)
        self.assertIn("Cloud Computing", rendered)
        self.assertIn("Southeast Asia", rendered)
        
        # Check that it's the correct phase
        self.assertIn("Phase 2: Executive Summary & Key Insights", rendered)
    
    def test_render_finalization(self):
        """Test rendering the finalization template."""
        rendered = self.manager.render_finalization(self.test_variables)
        
        # Check that variables were properly inserted
        self.assertIn("TechCorp", rendered)
        self.assertIn("Cloud Computing", rendered)
        self.assertIn("Southeast Asia", rendered)
        
        # Check that it's the finalization phase
        self.assertIn("Finalization: Complete Slide Deck", rendered)
    
    def test_missing_required_variables(self):
        """Test that an error is raised when required variables are missing."""
        incomplete_variables = {
            "company_name": "TechCorp",
            # Missing other required variables
        }
        
        with self.assertRaises(ValueError):
            self.manager.render_base_prompt(incomplete_variables)
    
    def test_invalid_phase_number(self):
        """Test that an error is raised when an invalid phase number is provided."""
        with self.assertRaises(ValueError):
            self.manager.render_phase(1, self.test_variables)  # Phase 1 is the base prompt
        
        with self.assertRaises(ValueError):
            self.manager.render_phase(7, self.test_variables)  # Only phases 2-6 exist


if __name__ == "__main__":
    unittest.main() 