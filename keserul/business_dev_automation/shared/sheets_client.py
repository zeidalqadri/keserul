"""
Google Sheets API client for Business Development Automation System.
Replaces MongoDB as the primary data store with proper rate limiting and error handling.
"""

import json
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

try:
    import gspread
    from google.auth.service_account import Credentials
    from gspread.exceptions import APIError, SpreadsheetNotFound
except ImportError:
    gspread = None
    Credentials = None
    APIError = Exception
    SpreadsheetNotFound = Exception

logger = logging.getLogger(__name__)


class SheetsClient:
    """Google Sheets API client with rate limiting and error handling."""
    
    def __init__(self, credentials_path: str, spreadsheet_id: str):
        """
        Initialize Google Sheets client.
        
        Args:
            credentials_path: Path to service account JSON file
            spreadsheet_id: Google Sheets spreadsheet ID
        """
        if not gspread:
            raise ImportError("gspread and google-auth libraries required")
            
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.client = None
        self.spreadsheet = None
        self._last_request_time = 0
        self._request_count = 0
        self._rate_limit_window = 100  # seconds
        self._max_requests_per_window = 90  # Leave buffer under 100 limit
        
        self._connect()
    
    def _connect(self):
        """Establish connection to Google Sheets."""
        try:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
            
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = Credentials.from_service_account_file(
                self.credentials_path, scopes=scope
            )
            
            self.client = gspread.authorize(credentials)
            self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            
            logger.info(f"Connected to Google Sheets: {self.spreadsheet.title}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            raise
    
    def _rate_limit(self):
        """Implement rate limiting for Google Sheets API."""
        current_time = time.time()
        
        # Reset counter if window has passed
        if current_time - self._last_request_time > self._rate_limit_window:
            self._request_count = 0
            self._last_request_time = current_time
        
        # Check if we're approaching rate limit
        if self._request_count >= self._max_requests_per_window:
            sleep_time = self._rate_limit_window - (current_time - self._last_request_time) + 1
            logger.warning(f"Rate limit approached, sleeping for {sleep_time:.1f} seconds")
            time.sleep(sleep_time)
            self._request_count = 0
            self._last_request_time = time.time()
        
        self._request_count += 1
    
    def _retry_on_error(self, func, *args, max_retries=3, **kwargs):
        """Retry function on API errors with exponential backoff."""
        for attempt in range(max_retries):
            try:
                self._rate_limit()
                return func(*args, **kwargs)
            except APIError as e:
                if attempt == max_retries - 1:
                    raise
                
                wait_time = (2 ** attempt) + (time.time() % 1)  # Add jitter
                logger.warning(f"API error on attempt {attempt + 1}: {e}. Retrying in {wait_time:.1f}s")
                time.sleep(wait_time)
            except Exception as e:
                logger.error(f"Non-recoverable error: {e}")
                raise
    
    def _get_worksheet(self, name: str):
        """Get or create worksheet by name."""
        try:
            return self.spreadsheet.worksheet(name)
        except gspread.WorksheetNotFound:
            logger.info(f"Creating worksheet: {name}")
            return self.spreadsheet.add_worksheet(title=name, rows=1000, cols=20)
    
    def write_contacts(self, contacts_data: List[Dict[str, Any]]) -> bool:
        """
        Write contacts data to the Contacts worksheet.
        
        Args:
            contacts_data: List of contact dictionaries
            
        Returns:
            bool: Success status
        """
        try:
            worksheet = self._get_worksheet("Contacts")
            
            # Define headers
            headers = [
                'id', 'name', 'role', 'company', 'email', 'linkedin_url', 
                'source', 'scraped_date', 'status', 'created_at'
            ]
            
            # Check if headers exist, if not add them
            if not worksheet.get_all_values():
                self._retry_on_error(worksheet.append_row, headers)
            
            # Prepare data rows
            rows = []
            for contact in contacts_data:
                row = [
                    contact.get('id', ''),
                    contact.get('name', ''),
                    contact.get('role', ''),
                    contact.get('company', ''),
                    contact.get('email', ''),
                    contact.get('linkedin_url', ''),
                    contact.get('source', ''),
                    contact.get('scraped_date', datetime.now().isoformat()),
                    contact.get('status', 'active'),
                    datetime.now().isoformat()
                ]
                rows.append(row)
            
            # Batch write for efficiency
            if rows:
                self._retry_on_error(worksheet.append_rows, rows)
                logger.info(f"Successfully wrote {len(rows)} contacts to Google Sheets")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to write contacts: {e}")
            return False
    
    def read_contacts(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Read contacts from the Contacts worksheet.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            List of contact dictionaries
        """
        try:
            worksheet = self._get_worksheet("Contacts")
            data = self._retry_on_error(worksheet.get_all_records)
            
            contacts = []
            for row in data:
                if not row.get('name'):  # Skip empty rows
                    continue
                    
                contact = {
                    'id': row.get('id', ''),
                    'name': row.get('name', ''),
                    'role': row.get('role', ''),
                    'company': row.get('company', ''),
                    'email': row.get('email', ''),
                    'linkedin_url': row.get('linkedin_url', ''),
                    'source': row.get('source', ''),
                    'scraped_date': row.get('scraped_date', ''),
                    'status': row.get('status', 'active'),
                    'created_at': row.get('created_at', '')
                }
                
                # Apply filters if provided
                if filters:
                    match = True
                    for key, value in filters.items():
                        if contact.get(key) != value:
                            match = False
                            break
                    if not match:
                        continue
                
                contacts.append(contact)
            
            logger.info(f"Read {len(contacts)} contacts from Google Sheets")
            return contacts
            
        except Exception as e:
            logger.error(f"Failed to read contacts: {e}")
            return []
    
    def write_outreach_log(self, outreach_data: List[Dict[str, Any]]) -> bool:
        """
        Write outreach log data to the Outreach_Log worksheet.
        
        Args:
            outreach_data: List of outreach log dictionaries
            
        Returns:
            bool: Success status
        """
        try:
            worksheet = self._get_worksheet("Outreach_Log")
            
            # Define headers
            headers = [
                'id', 'contact_id', 'contact_name', 'contact_company',
                'message_type', 'subject', 'sent_date', 'delivery_status', 
                'response_status', 'created_at'
            ]
            
            # Check if headers exist, if not add them
            if not worksheet.get_all_values():
                self._retry_on_error(worksheet.append_row, headers)
            
            # Prepare data rows
            rows = []
            for log_entry in outreach_data:
                row = [
                    log_entry.get('id', ''),
                    log_entry.get('contact_id', ''),
                    log_entry.get('contact_name', ''),
                    log_entry.get('contact_company', ''),
                    log_entry.get('message_type', ''),
                    log_entry.get('subject', ''),
                    log_entry.get('sent_date', datetime.now().isoformat()),
                    log_entry.get('delivery_status', 'pending'),
                    log_entry.get('response_status', 'none'),
                    datetime.now().isoformat()
                ]
                rows.append(row)
            
            # Batch write for efficiency
            if rows:
                self._retry_on_error(worksheet.append_rows, rows)
                logger.info(f"Successfully wrote {len(rows)} outreach logs to Google Sheets")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to write outreach logs: {e}")
            return False
    
    def update_outreach_status(self, contact_id: str, status: str) -> bool:
        """
        Update outreach status for a specific contact.
        
        Args:
            contact_id: Contact ID to update
            status: New status value
            
        Returns:
            bool: Success status
        """
        try:
            worksheet = self._get_worksheet("Outreach_Log")
            data = self._retry_on_error(worksheet.get_all_records)
            
            # Find the row to update
            for i, row in enumerate(data, start=2):  # Start from row 2 (after header)
                if row.get('contact_id') == contact_id:
                    self._retry_on_error(worksheet.update_cell, i, 8, status)  # Column 8 is delivery_status
                    logger.info(f"Updated outreach status for contact {contact_id} to {status}")
                    return True
            
            logger.warning(f"Contact {contact_id} not found in outreach log")
            return False
            
        except Exception as e:
            logger.error(f"Failed to update outreach status: {e}")
            return False
    
    def write_market_insights(self, insights_data: List[Dict[str, Any]]) -> bool:
        """
        Write market insights to the Market_Insights worksheet.
        
        Args:
            insights_data: List of market insight dictionaries
            
        Returns:
            bool: Success status
        """
        try:
            worksheet = self._get_worksheet("Market_Insights")
            
            # Define headers
            headers = [
                'id', 'query', 'research_date', 'findings', 'summary',
                'source', 'region', 'industry', 'created_at'
            ]
            
            # Check if headers exist, if not add them
            if not worksheet.get_all_values():
                self._retry_on_error(worksheet.append_row, headers)
            
            # Prepare data rows
            rows = []
            for insight in insights_data:
                row = [
                    insight.get('id', ''),
                    insight.get('query', ''),
                    insight.get('research_date', datetime.now().isoformat()),
                    insight.get('findings', ''),
                    insight.get('summary', ''),
                    insight.get('source', 'perplexity'),
                    insight.get('region', ''),
                    insight.get('industry', ''),
                    datetime.now().isoformat()
                ]
                rows.append(row)
            
            # Batch write for efficiency
            if rows:
                self._retry_on_error(worksheet.append_rows, rows)
                logger.info(f"Successfully wrote {len(rows)} market insights to Google Sheets")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to write market insights: {e}")
            return False
    
    def read_market_insights(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Read market insights from the Market_Insights worksheet.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            List of market insight dictionaries
        """
        try:
            worksheet = self._get_worksheet("Market_Insights")
            data = self._retry_on_error(worksheet.get_all_records)
            
            insights = []
            for row in data:
                if not row.get('query'):  # Skip empty rows
                    continue
                    
                insight = {
                    'id': row.get('id', ''),
                    'query': row.get('query', ''),
                    'research_date': row.get('research_date', ''),
                    'findings': row.get('findings', ''),
                    'summary': row.get('summary', ''),
                    'source': row.get('source', ''),
                    'region': row.get('region', ''),
                    'industry': row.get('industry', ''),
                    'created_at': row.get('created_at', '')
                }
                
                # Apply filters if provided
                if filters:
                    match = True
                    for key, value in filters.items():
                        if insight.get(key) != value:
                            match = False
                            break
                    if not match:
                        continue
                
                insights.append(insight)
            
            logger.info(f"Read {len(insights)} market insights from Google Sheets")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to read market insights: {e}")
            return []
    
    def write_strategy_reports(self, reports_data: List[Dict[str, Any]]) -> bool:
        """
        Write strategy reports to the Strategy_Reports worksheet.
        
        Args:
            reports_data: List of strategy report dictionaries
            
        Returns:
            bool: Success status
        """
        try:
            worksheet = self._get_worksheet("Strategy_Reports")
            
            # Define headers
            headers = [
                'id', 'company', 'analysis_date', 'mckinsey_framework',
                'recommendations', 'deck_path', 'executive_summary',
                'created_at'
            ]
            
            # Check if headers exist, if not add them
            if not worksheet.get_all_values():
                self._retry_on_error(worksheet.append_row, headers)
            
            # Prepare data rows
            rows = []
            for report in reports_data:
                row = [
                    report.get('id', ''),
                    report.get('company', ''),
                    report.get('analysis_date', datetime.now().isoformat()),
                    report.get('mckinsey_framework', ''),
                    report.get('recommendations', ''),
                    report.get('deck_path', ''),
                    report.get('executive_summary', ''),
                    datetime.now().isoformat()
                ]
                rows.append(row)
            
            # Batch write for efficiency
            if rows:
                self._retry_on_error(worksheet.append_rows, rows)
                logger.info(f"Successfully wrote {len(rows)} strategy reports to Google Sheets")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to write strategy reports: {e}")
            return False
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of Google Sheets connection.
        
        Returns:
            Dict with health status information
        """
        try:
            # Test connection by getting spreadsheet title
            title = self._retry_on_error(lambda: self.spreadsheet.title)
            
            return {
                'status': 'healthy',
                'spreadsheet_title': title,
                'spreadsheet_id': self.spreadsheet_id,
                'last_check': datetime.now().isoformat(),
                'request_count': self._request_count
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }


# Factory function for easy instantiation
def create_sheets_client(credentials_path: str = None, spreadsheet_id: str = None) -> SheetsClient:
    """
    Create a SheetsClient instance with environment variable fallbacks.
    
    Args:
        credentials_path: Path to service account JSON (defaults to env var)
        spreadsheet_id: Google Sheets ID (defaults to env var)
        
    Returns:
        Configured SheetsClient instance
    """
    if not credentials_path:
        credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH', 
                                   './credentials/sheets-service-account.json')
    
    if not spreadsheet_id:
        spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        if not spreadsheet_id:
            raise ValueError("GOOGLE_SHEETS_SPREADSHEET_ID environment variable required")
    
    return SheetsClient(credentials_path, spreadsheet_id) 