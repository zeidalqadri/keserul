#!/usr/bin/env python3
"""
Setup script for Google Sheets integration.
Creates the required worksheets and configures the spreadsheet structure.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from shared.sheets_client import SheetsClient
except ImportError:
    print("Error: Could not import SheetsClient. Make sure dependencies are installed.")
    print("Run: pip install gspread google-auth")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GoogleSheetsSetup:
    """Setup and configure Google Sheets for Business Development Automation."""
    
    def __init__(self, credentials_path: str, spreadsheet_id: Optional[str] = None):
        """
        Initialize setup with credentials and optional spreadsheet ID.
        
        Args:
            credentials_path: Path to service account JSON file
            spreadsheet_id: Existing spreadsheet ID (optional, will create new if not provided)
        """
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.client: Optional[SheetsClient] = None
        
    def validate_credentials(self) -> bool:
        """Validate the credentials file exists and is properly formatted."""
        try:
            if not Path(self.credentials_path).exists():
                logger.error(f"Credentials file not found: {self.credentials_path}")
                return False
            
            with open(self.credentials_path, 'r') as f:
                creds = json.load(f)
            
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in creds]
            
            if missing_fields:
                logger.error(f"Missing required fields in credentials: {missing_fields}")
                return False
            
            if creds.get('type') != 'service_account':
                logger.error("Credentials must be for a service account")
                return False
            
            logger.info("✓ Credentials file is valid")
            return True
            
        except json.JSONDecodeError:
            logger.error("Credentials file is not valid JSON")
            return False
        except Exception as e:
            logger.error(f"Error validating credentials: {e}")
            return False
    
    def create_spreadsheet(self, title: str = "Business Development Automation") -> str:
        """
        Create a new Google Spreadsheet.
        
        Args:
            title: Title for the new spreadsheet
            
        Returns:
            Spreadsheet ID of created spreadsheet
        """
        try:
            import gspread
            from google.auth.service_account import Credentials
            
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = Credentials.from_service_account_file(
                self.credentials_path, scopes=scope
            )
            
            client = gspread.authorize(credentials)
            spreadsheet = client.create(title)
            
            logger.info(f"✓ Created new spreadsheet: {title}")
            logger.info(f"✓ Spreadsheet ID: {spreadsheet.id}")
            logger.info(f"✓ URL: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")
            
            return spreadsheet.id
            
        except Exception as e:
            logger.error(f"Failed to create spreadsheet: {e}")
            raise
    
    def setup_worksheets(self) -> bool:
        """
        Create and configure all required worksheets.
        
        Returns:
            bool: Success status
        """
        try:
            if not self.spreadsheet_id:
                logger.error("Spreadsheet ID is required to setup worksheets")
                return False
            
            self.client = SheetsClient(self.credentials_path, self.spreadsheet_id)
            
            worksheets = [
                {
                    'name': 'Contacts',
                    'headers': [
                        'id', 'name', 'role', 'company', 'email', 'linkedin_url',
                        'source', 'scraped_date', 'status', 'created_at'
                    ]
                },
                {
                    'name': 'Outreach_Log',
                    'headers': [
                        'id', 'contact_id', 'contact_name', 'contact_company',
                        'message_type', 'subject', 'sent_date', 'delivery_status',
                        'response_status', 'created_at'
                    ]
                },
                {
                    'name': 'Market_Insights',
                    'headers': [
                        'id', 'query', 'research_date', 'findings', 'summary',
                        'source', 'region', 'industry', 'created_at'
                    ]
                },
                {
                    'name': 'Strategy_Reports',
                    'headers': [
                        'id', 'company', 'analysis_date', 'mckinsey_framework',
                        'recommendations', 'deck_path', 'executive_summary',
                        'created_at'
                    ]
                }
            ]
            
            for worksheet_config in worksheets:
                self._setup_worksheet(worksheet_config['name'], worksheet_config['headers'])
            
            logger.info("✓ All worksheets created and configured successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup worksheets: {e}")
            return False
    
    def _setup_worksheet(self, name: str, headers: list) -> bool:
        """
        Setup individual worksheet with headers and formatting.
        
        Args:
            name: Worksheet name
            headers: List of column headers
            
        Returns:
            bool: Success status
        """
        try:
            # Get or create worksheet
            worksheet = self.client._get_worksheet(name)
            
            # Clear existing content
            worksheet.clear()
            
            # Add headers
            worksheet.append_row(headers)
            
            # Format headers (bold, background color)
            header_range = f"A1:{chr(65 + len(headers) - 1)}1"
            worksheet.format(header_range, {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}
            })
            
            # Freeze header row
            worksheet.freeze(rows=1)
            
            # Auto-resize columns
            worksheet.columns_auto_resize(0, len(headers) - 1)
            
            logger.info(f"✓ Configured worksheet: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup worksheet {name}: {e}")
            return False
    
    def test_integration(self) -> bool:
        """
        Test the Google Sheets integration by writing and reading test data.
        
        Returns:
            bool: Success status
        """
        try:
            if not self.client:
                self.client = SheetsClient(self.credentials_path, self.spreadsheet_id)
            
            # Test contact write/read
            test_contact = [{
                'id': 'test-contact-1',
                'name': 'Test User',
                'role': 'Software Engineer',
                'company': 'Test Corp',
                'email': 'test@testcorp.com',
                'linkedin_url': 'https://linkedin.com/in/testuser',
                'source': 'test'
            }]
            
            if not self.client.write_contacts(test_contact):
                logger.error("Failed to write test contact")
                return False
            
            contacts = self.client.read_contacts({'source': 'test'})
            if not contacts or len(contacts) != 1:
                logger.error("Failed to read test contact")
                return False
            
            # Test market insight write
            test_insight = [{
                'id': 'test-insight-1',
                'query': 'Test market research query',
                'findings': 'Test findings data',
                'summary': 'Test summary',
                'source': 'test',
                'region': 'Global',
                'industry': 'Testing'
            }]
            
            if not self.client.write_market_insights(test_insight):
                logger.error("Failed to write test market insight")
                return False
            
            insights = self.client.read_market_insights({'source': 'test'})
            if not insights or len(insights) != 1:
                logger.error("Failed to read test market insight")
                return False
            
            logger.info("✓ Integration test passed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Integration test failed: {e}")
            return False
    
    def get_health_status(self) -> dict:
        """
        Get comprehensive health status of the Google Sheets setup.
        
        Returns:
            dict: Health status information
        """
        if not self.client:
            self.client = SheetsClient(self.credentials_path, self.spreadsheet_id)
        
        return self.client.get_health_status()


def main():
    """Main setup function with command-line interface."""
    parser = argparse.ArgumentParser(description='Setup Google Sheets for Business Development Automation')
    parser.add_argument('--credentials', required=True, help='Path to service account JSON file')
    parser.add_argument('--spreadsheet-id', help='Existing spreadsheet ID (optional)')
    parser.add_argument('--create-new', action='store_true', help='Create a new spreadsheet')
    parser.add_argument('--title', default='Business Development Automation', help='Title for new spreadsheet')
    parser.add_argument('--test', action='store_true', help='Run integration tests after setup')
    
    args = parser.parse_args()
    
    setup = GoogleSheetsSetup(args.credentials, args.spreadsheet_id)
    
    # Validate credentials
    if not setup.validate_credentials():
        logger.error("Credentials validation failed")
        sys.exit(1)
    
    # Create new spreadsheet if requested
    if args.create_new:
        try:
            spreadsheet_id = setup.create_spreadsheet(args.title)
            setup.spreadsheet_id = spreadsheet_id
            
            # Print environment variable for easy copy/paste
            print(f"\n✓ Add this to your .env file:")
            print(f"GOOGLE_SHEETS_SPREADSHEET_ID={spreadsheet_id}")
            
        except Exception as e:
            logger.error(f"Failed to create spreadsheet: {e}")
            sys.exit(1)
    
    # Setup worksheets
    if setup.spreadsheet_id:
        if not setup.setup_worksheets():
            logger.error("Worksheet setup failed")
            sys.exit(1)
        
        # Run integration tests if requested
        if args.test:
            if not setup.test_integration():
                logger.error("Integration tests failed")
                sys.exit(1)
        
        # Print health status
        health = setup.get_health_status()
        print(f"\n✓ Setup completed successfully!")
        print(f"✓ Spreadsheet: {health.get('spreadsheet_title', 'Unknown')}")
        print(f"✓ Status: {health.get('status', 'Unknown')}")
        print(f"✓ URL: https://docs.google.com/spreadsheets/d/{setup.spreadsheet_id}")
    
    else:
        logger.error("No spreadsheet ID provided. Use --create-new or --spreadsheet-id")
        sys.exit(1)


if __name__ == '__main__':
    main() 