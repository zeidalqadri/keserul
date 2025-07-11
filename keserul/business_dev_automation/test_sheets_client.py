"""
Test suite for Google Sheets client module.
Tests both mocked functionality and basic integration patterns.
"""

import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from shared.sheets_client import SheetsClient, create_sheets_client


class TestSheetsClient:
    """Test cases for SheetsClient functionality."""
    
    @pytest.fixture
    def mock_credentials_path(self, tmp_path):
        """Create a temporary credentials file for testing."""
        credentials = {
            "type": "service_account",
            "project_id": "test-project",
            "private_key_id": "test-key-id",
            "private_key": "-----BEGIN PRIVATE KEY-----\ntest-key\n-----END PRIVATE KEY-----\n",
            "client_email": "test@test-project.iam.gserviceaccount.com",
            "client_id": "test-client-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
        
        creds_file = tmp_path / "test-credentials.json"
        creds_file.write_text(json.dumps(credentials))
        return str(creds_file)
    
    @pytest.fixture
    def mock_gspread(self):
        """Mock gspread and related dependencies."""
        with patch('shared.sheets_client.gspread') as mock_gs, \
             patch('shared.sheets_client.Credentials') as mock_creds:
            
            # Mock spreadsheet and worksheet
            mock_worksheet = Mock()
            mock_worksheet.get_all_values.return_value = [['name', 'role', 'company']]
            mock_worksheet.get_all_records.return_value = []
            mock_worksheet.append_row.return_value = None
            mock_worksheet.append_rows.return_value = None
            
            mock_spreadsheet = Mock()
            mock_spreadsheet.title = "Test Spreadsheet"
            mock_spreadsheet.worksheet.return_value = mock_worksheet
            mock_spreadsheet.add_worksheet.return_value = mock_worksheet
            
            mock_client = Mock()
            mock_client.open_by_key.return_value = mock_spreadsheet
            
            mock_gs.authorize.return_value = mock_client
            mock_creds.from_service_account_file.return_value = Mock()
            
            yield mock_gs, mock_creds, mock_client, mock_spreadsheet, mock_worksheet
    
    def test_client_initialization(self, mock_gspread, mock_credentials_path):
        """Test successful client initialization."""
        mock_gs, mock_creds, mock_client, mock_spreadsheet, mock_worksheet = mock_gspread
        
        client = SheetsClient(mock_credentials_path, "test-spreadsheet-id")
        
        assert client.spreadsheet_id == "test-spreadsheet-id"
        assert client.client is not None
        assert client.spreadsheet is not None
        mock_creds.from_service_account_file.assert_called_once()
        mock_gs.authorize.assert_called_once()
    
    def test_client_initialization_missing_credentials(self):
        """Test client initialization with missing credentials file."""
        with pytest.raises(FileNotFoundError):
            SheetsClient("/nonexistent/path.json", "test-id")
    
    def test_rate_limiting_mechanism(self, mock_gspread, mock_credentials_path):
        """Test rate limiting functionality."""
        mock_gs, mock_creds, mock_client, mock_spreadsheet, mock_worksheet = mock_gspread
        
        client = SheetsClient(mock_credentials_path, "test-id")
        
        # Simulate approaching rate limit
        client._request_count = 89
        client._last_request_time = client._last_request_time
        
        with patch('time.sleep') as mock_sleep:
            client._rate_limit()
            # Should not sleep yet
            mock_sleep.assert_not_called()
        
        # Simulate hitting rate limit
        client._request_count = 90
        
        with patch('time.sleep') as mock_sleep:
            client._rate_limit()
            # Should sleep when limit is hit
            mock_sleep.assert_called_once()
    
    def test_write_contacts_success(self, mock_gspread, mock_credentials_path):
        """Test successful contacts write operation."""
        mock_gs, mock_creds, mock_client, mock_spreadsheet, mock_worksheet = mock_gspread
        
        client = SheetsClient(mock_credentials_path, "test-id")
        
        contacts_data = [
            {
                'id': 'contact-1',
                'name': 'John Doe',
                'role': 'Software Engineer',
                'company': 'Tech Corp',
                'email': 'john@techcorp.com',
                'linkedin_url': 'https://linkedin.com/in/johndoe',
                'source': 'sgtech'
            }
        ]
        
        result = client.write_contacts(contacts_data)
        
        assert result is True
        mock_worksheet.append_rows.assert_called_once()
        
        # Verify the data structure
        call_args = mock_worksheet.append_rows.call_args[0][0]
        assert len(call_args) == 1  # One contact
        assert call_args[0][0] == 'contact-1'  # ID
        assert call_args[0][1] == 'John Doe'   # Name
    
    def test_read_contacts_success(self, mock_gspread, mock_credentials_path):
        """Test successful contacts read operation."""
        mock_gs, mock_creds, mock_client, mock_spreadsheet, mock_worksheet = mock_gspread
        
        # Mock return data
        mock_worksheet.get_all_records.return_value = [
            {
                'id': 'contact-1',
                'name': 'John Doe',
                'role': 'Engineer',
                'company': 'Tech Corp',
                'email': 'john@techcorp.com',
                'linkedin_url': 'https://linkedin.com/in/johndoe',
                'source': 'sgtech',
                'scraped_date': '2025-01-13',
                'status': 'active',
                'created_at': '2025-01-13T10:00:00'
            }
        ]
        
        client = SheetsClient(mock_credentials_path, "test-id")
        contacts = client.read_contacts()
        
        assert len(contacts) == 1
        assert contacts[0]['name'] == 'John Doe'
        assert contacts[0]['company'] == 'Tech Corp'
    
    def test_read_contacts_with_filters(self, mock_gspread, mock_credentials_path):
        """Test contacts read operation with filters."""
        mock_gs, mock_creds, mock_client, mock_spreadsheet, mock_worksheet = mock_gspread
        
        # Mock return data with multiple contacts
        mock_worksheet.get_all_records.return_value = [
            {
                'id': 'contact-1',
                'name': 'John Doe',
                'company': 'Tech Corp',
                'status': 'active',
                'role': '', 'email': '', 'linkedin_url': '', 'source': '', 
                'scraped_date': '', 'created_at': ''
            },
            {
                'id': 'contact-2', 
                'name': 'Jane Smith',
                'company': 'Design Inc',
                'status': 'inactive',
                'role': '', 'email': '', 'linkedin_url': '', 'source': '',
                'scraped_date': '', 'created_at': ''
            }
        ]
        
        client = SheetsClient(mock_credentials_path, "test-id")
        
        # Test filter by status
        active_contacts = client.read_contacts({'status': 'active'})
        assert len(active_contacts) == 1
        assert active_contacts[0]['name'] == 'John Doe'
        
        # Test filter by company
        tech_contacts = client.read_contacts({'company': 'Tech Corp'})
        assert len(tech_contacts) == 1
        assert tech_contacts[0]['name'] == 'John Doe'
    
    def test_write_outreach_log_success(self, mock_gspread, mock_credentials_path):
        """Test successful outreach log write operation.""" 
        mock_gs, mock_creds, mock_client, mock_spreadsheet, mock_worksheet = mock_gspread
        
        client = SheetsClient(mock_credentials_path, "test-id")
        
        outreach_data = [
            {
                'id': 'outreach-1',
                'contact_id': 'contact-1', 
                'contact_name': 'John Doe',
                'contact_company': 'Tech Corp',
                'message_type': 'introduction',
                'subject': 'Partnership Opportunity',
                'delivery_status': 'sent',
                'response_status': 'pending'
            }
        ]
        
        result = client.write_outreach_log(outreach_data)
        
        assert result is True
        mock_worksheet.append_rows.assert_called_once()
    
    def test_write_market_insights_success(self, mock_gspread, mock_credentials_path):
        """Test successful market insights write operation."""
        mock_gs, mock_creds, mock_client, mock_spreadsheet, mock_worksheet = mock_gspread
        
        client = SheetsClient(mock_credentials_path, "test-id")
        
        insights_data = [
            {
                'id': 'insight-1',
                'query': 'Singapore tech market trends',
                'findings': 'Growing demand for AI tools',
                'summary': 'Market expanding rapidly',
                'source': 'perplexity',
                'region': 'Singapore',
                'industry': 'Technology'
            }
        ]
        
        result = client.write_market_insights(insights_data)
        
        assert result is True
        mock_worksheet.append_rows.assert_called_once()
    
    def test_error_handling_api_failure(self, mock_gspread, mock_credentials_path):
        """Test error handling when API calls fail."""
        mock_gs, mock_creds, mock_client, mock_spreadsheet, mock_worksheet = mock_gspread
        
        # Mock API error
        from gspread.exceptions import APIError
        mock_worksheet.append_rows.side_effect = APIError("Rate limit exceeded")
        
        client = SheetsClient(mock_credentials_path, "test-id")
        
        contacts_data = [{'name': 'Test User'}]
        result = client.write_contacts(contacts_data)
        
        assert result is False
    
    def test_retry_mechanism(self, mock_gspread, mock_credentials_path):
        """Test retry mechanism for transient failures."""
        mock_gs, mock_creds, mock_client, mock_spreadsheet, mock_worksheet = mock_gspread
        
        client = SheetsClient(mock_credentials_path, "test-id")
        
        # Mock function that fails twice then succeeds
        mock_func = Mock()
        mock_func.side_effect = [Exception("Transient error"), Exception("Another error"), "Success"]
        
        with patch('time.sleep'):  # Speed up test
            result = client._retry_on_error(mock_func, max_retries=3)
        
        assert result == "Success"
        assert mock_func.call_count == 3
    
    def test_health_status_healthy(self, mock_gspread, mock_credentials_path):
        """Test health status check when system is healthy."""
        mock_gs, mock_creds, mock_client, mock_spreadsheet, mock_worksheet = mock_gspread
        
        client = SheetsClient(mock_credentials_path, "test-id")
        health = client.get_health_status()
        
        assert health['status'] == 'healthy'
        assert health['spreadsheet_title'] == 'Test Spreadsheet'
        assert 'last_check' in health
    
    def test_health_status_unhealthy(self, mock_gspread, mock_credentials_path):
        """Test health status check when system is unhealthy."""
        mock_gs, mock_creds, mock_client, mock_spreadsheet, mock_worksheet = mock_gspread
        
        # Mock spreadsheet access failure
        mock_spreadsheet.title = property(lambda self: (_ for _ in ()).throw(Exception("Connection failed")))
        
        client = SheetsClient(mock_credentials_path, "test-id")
        health = client.get_health_status()
        
        assert health['status'] == 'unhealthy'
        assert 'error' in health


class TestFactoryFunction:
    """Test cases for the factory function."""
    
    def test_create_sheets_client_with_params(self, tmp_path):
        """Test factory function with explicit parameters."""
        # Create mock credentials file
        creds_file = tmp_path / "test-creds.json"
        creds_file.write_text('{"type": "service_account"}')
        
        with patch('shared.sheets_client.SheetsClient') as mock_sheets_client:
            create_sheets_client(str(creds_file), "test-spreadsheet-id")
            mock_sheets_client.assert_called_once_with(str(creds_file), "test-spreadsheet-id")
    
    def test_create_sheets_client_with_env_vars(self):
        """Test factory function using environment variables."""
        with patch('shared.sheets_client.SheetsClient') as mock_sheets_client, \
             patch.dict(os.environ, {
                 'GOOGLE_SHEETS_CREDENTIALS_PATH': '/path/to/creds.json',
                 'GOOGLE_SHEETS_SPREADSHEET_ID': 'env-spreadsheet-id'
             }):
            
            create_sheets_client()
            mock_sheets_client.assert_called_once_with('/path/to/creds.json', 'env-spreadsheet-id')
    
    def test_create_sheets_client_missing_spreadsheet_id(self):
        """Test factory function fails without spreadsheet ID."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="GOOGLE_SHEETS_SPREADSHEET_ID"):
                create_sheets_client()


if __name__ == '__main__':
    pytest.main([__file__]) 