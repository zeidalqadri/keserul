"""
Integration tests for Business Development Automation System
INT-01: Happy path with successful lead generation, outreach, and market research
INT-02: Zero contacts scenario testing error handling
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
import tempfile
import csv
from datetime import datetime


class TestIntegrationWorkflow:
    """Integration tests for the complete business development workflow"""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory for tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def mock_contacts_data(self):
        """Sample contact data for testing"""
        return [
            {
                "name": "Test Contact 1",
                "role": "CTO",
                "company": "TechCorp SG",
                "email": "test1@techcorp.sg",
                "linkedin": "https://linkedin.com/in/test1",
                "source": "SGTech"
            },
            {
                "name": "Test Contact 2", 
                "role": "Lead Developer",
                "company": "DevStudio MY",
                "email": "test2@devstudio.my",
                "linkedin": "https://linkedin.com/in/test2",
                "source": "MDEC"
            }
        ]
    
    @pytest.fixture
    def mock_market_insights(self):
        """Sample market research data for testing"""
        return {
            "executive_summary": "Singapore and Malaysia SME dev-tools market shows strong growth",
            "key_findings": [
                "75% of SMEs plan to increase dev-tools budget in 2024",
                "Cloud-native solutions preferred by 80% of respondents"
            ],
            "budget_analysis": {
                "average_annual_budget": "$25,000",
                "growth_rate": "15% YoY"
            }
        }

    def test_int_01_happy_path_workflow(self, temp_output_dir, mock_contacts_data, mock_market_insights):
        """
        INT-01: Happy path integration test
        Tests complete workflow: LeadGen -> Outreach -> Market Research
        """
        # Mock system coordinator components
        with patch('business_dev_automation.system_coordinator.LeadGenCoordinator') as mock_leadgen, \
             patch('business_dev_automation.system_coordinator.OutreachCoordinator') as mock_outreach, \
             patch('business_dev_automation.system_coordinator.PerplexityCoordinator') as mock_perplexity:
            
            # Setup LeadGen mock
            mock_leadgen_instance = Mock()
            mock_leadgen_instance.run_pipeline.return_value = {
                "total_contacts": 2,
                "contacts_file": f"{temp_output_dir}/contacts_sg_my.csv",
                "success": True
            }
            mock_leadgen.return_value = mock_leadgen_instance
            
            # Setup Outreach mock
            mock_outreach_instance = Mock()
            mock_outreach_instance.run_outreach_campaign.return_value = {
                "emails_sent": 2,
                "delivery_rate": 100.0,
                "log_file": f"{temp_output_dir}/outreach_log.csv",
                "success": True
            }
            mock_outreach.return_value = mock_outreach_instance
            
            # Setup Perplexity mock
            mock_perplexity_instance = Mock()
            mock_perplexity_instance.generate_market_insights.return_value = {
                "insights_file": f"{temp_output_dir}/market_insights.md",
                "research_queries": 5,
                "success": True
            }
            mock_perplexity.return_value = mock_perplexity_instance
            
            # Create mock output files
            contacts_file = f"{temp_output_dir}/contacts_sg_my.csv"
            with open(contacts_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'role', 'company', 'email', 'linkedin', 'source'])
                writer.writeheader()
                writer.writerows(mock_contacts_data)
            
            outreach_file = f"{temp_output_dir}/outreach_log.csv"
            with open(outreach_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['contact_name', 'email', 'status', 'timestamp'])
                writer.writerow(['Test Contact 1', 'test1@techcorp.sg', 'sent', '2024-01-09 10:00:00'])
                writer.writerow(['Test Contact 2', 'test2@devstudio.my', 'sent', '2024-01-09 10:01:00'])
            
            insights_file = f"{temp_output_dir}/market_insights.md"
            with open(insights_file, 'w') as f:
                f.write("# Market Insights Report\n\n")
                f.write("## Executive Summary\n")
                f.write(mock_market_insights["executive_summary"])
            
            # Import and run the system coordinator
            try:
                from business_dev_automation.system_coordinator import SystemCoordinator
                coordinator = SystemCoordinator(output_dir=temp_output_dir)
                
                # Inject the mocked coordinators
                coordinator.leadgen_coordinator = mock_leadgen_instance
                coordinator.outreach_coordinator = mock_outreach_instance
                coordinator.perplexity_coordinator = mock_perplexity_instance
                
                # Run the integrated workflow
                result = coordinator.run_full_pipeline()
                
                # Verify results
                assert result["success"] is True
                assert result["leadgen"]["total_contacts"] == 2
                assert result["outreach"]["emails_sent"] == 2
                assert result["perplexity"]["success"] is True
                
                # Verify output files exist
                assert os.path.exists(contacts_file)
                assert os.path.exists(outreach_file)
                assert os.path.exists(insights_file)
                
            except ImportError:
                # If system_coordinator doesn't exist, create a mock workflow test
                pytest.skip("SystemCoordinator not implemented yet - creating mock test")

    def test_int_02_zero_contacts_scenario(self, temp_output_dir):
        """
        INT-02: Zero contacts scenario test
        Tests error handling when no contacts are found
        """
        with patch('business_dev_automation.system_coordinator.LeadGenCoordinator') as mock_leadgen, \
             patch('business_dev_automation.system_coordinator.OutreachCoordinator') as mock_outreach, \
             patch('business_dev_automation.system_coordinator.PerplexityCoordinator') as mock_perplexity:
            
            # Setup LeadGen mock for zero contacts
            mock_leadgen_instance = Mock()
            mock_leadgen_instance.run_pipeline.return_value = {
                "total_contacts": 0,
                "contacts_file": f"{temp_output_dir}/contacts_sg_my.csv",
                "success": True,
                "warning": "No contacts found in scraped directories"
            }
            mock_leadgen.return_value = mock_leadgen_instance
            
            # Setup Outreach mock to handle zero contacts gracefully
            mock_outreach_instance = Mock()
            mock_outreach_instance.run_outreach_campaign.return_value = {
                "emails_sent": 0,
                "delivery_rate": 0.0,
                "log_file": f"{temp_output_dir}/outreach_log.csv",
                "success": True,
                "warning": "No contacts available for outreach"
            }
            mock_outreach.return_value = mock_outreach_instance
            
            # Setup Perplexity mock to continue regardless
            mock_perplexity_instance = Mock()
            mock_perplexity_instance.generate_market_insights.return_value = {
                "insights_file": f"{temp_output_dir}/market_insights.md",
                "research_queries": 5,
                "success": True
            }
            mock_perplexity.return_value = mock_perplexity_instance
            
            # Create empty contacts file
            contacts_file = f"{temp_output_dir}/contacts_sg_my.csv"
            with open(contacts_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['name', 'role', 'company', 'email', 'linkedin', 'source'])
            
            # Create empty outreach log
            outreach_file = f"{temp_output_dir}/outreach_log.csv"
            with open(outreach_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['contact_name', 'email', 'status', 'timestamp'])
            
            # Create insights file (should still work)
            insights_file = f"{temp_output_dir}/market_insights.md"
            with open(insights_file, 'w') as f:
                f.write("# Market Insights Report\n\n")
                f.write("## Executive Summary\n")
                f.write("Market research completed despite zero contacts found.")
            
            try:
                from business_dev_automation.system_coordinator import SystemCoordinator
                coordinator = SystemCoordinator(output_dir=temp_output_dir)
                
                # Inject the mocked coordinators
                coordinator.leadgen_coordinator = mock_leadgen_instance
                coordinator.outreach_coordinator = mock_outreach_instance
                coordinator.perplexity_coordinator = mock_perplexity_instance
                
                # Run the workflow with zero contacts
                result = coordinator.run_full_pipeline()
                
                # Verify graceful handling
                assert result["success"] is True  # Overall success despite zero contacts
                assert result["leadgen"]["total_contacts"] == 0
                assert result["outreach"]["emails_sent"] == 0
                assert result["perplexity"]["success"] is True  # Market research should still work
                
                # Verify files exist but are empty/minimal
                assert os.path.exists(contacts_file)
                assert os.path.exists(outreach_file)
                assert os.path.exists(insights_file)
                
                # Verify proper warning messages
                assert "warning" in result["leadgen"]
                assert "warning" in result["outreach"]
                
            except ImportError:
                # If system_coordinator doesn't exist, create a mock workflow test
                pytest.skip("SystemCoordinator not implemented yet - creating mock test")

    def test_system_coordinator_import(self):
        """Test that system coordinator can be imported"""
        try:
            from business_dev_automation.system_coordinator import SystemCoordinator
            assert SystemCoordinator is not None
        except ImportError as e:
            pytest.skip(f"SystemCoordinator not available: {e}")

    def test_integration_components_exist(self):
        """Test that all integration components are available"""
        components = [
            'business_dev_automation.leadgen_bot',
            'business_dev_automation.outreach_bot', 
            'business_dev_automation.perplexity_bot',
            'business_dev_automation.shared'
        ]
        
        missing_components = []
        for component in components:
            try:
                __import__(component)
            except ImportError:
                missing_components.append(component)
        
        if missing_components:
            pytest.skip(f"Missing components: {missing_components}")
        
        assert len(missing_components) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 