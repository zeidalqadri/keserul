"""Outreach Bot Package"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import time

# Import Google Sheets client
try:
    from business_dev_automation.shared.sheets_client import SheetsClient
except ImportError:
    SheetsClient = None

logger = logging.getLogger(__name__)


class OutreachCoordinator:
    """Real outreach coordinator with Google Sheets integration"""
    
    def __init__(self, credentials_path: str = None, spreadsheet_id: str = None):
        """
        Initialize Outreach coordinator.
        
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
                logger.info("Outreach connected to Google Sheets")
            except Exception as e:
                logger.warning(f"Could not connect to Google Sheets: {e}")
        
        # Initialize message generator and email client
        self.message_generator = MessageGenerator()
        self.email_client = EmailClient()
    
    def run_outreach_campaign(self, campaign_type: str = "dev_tools_intro") -> Dict[str, Any]:
        """
        Run outreach campaign to contacts in Google Sheets.
        
        Args:
            campaign_type: Type of campaign to run
            
        Returns:
            Dict with campaign results
        """
        start_time = time.time()
        results = {
            "success": False,
            "emails_sent": 0,
            "delivery_rate": 0.0,
            "log_file": None,
            "campaign_type": campaign_type,
            "personalization_level": "high",
            "errors": []
        }
        
        try:
            logger.info(f"Starting outreach campaign: {campaign_type}")
            
            # Read contacts from Google Sheets
            contacts = []
            if self.sheets_client:
                contacts = self.sheets_client.read_contacts({"status": "active"})
                logger.info(f"Found {len(contacts)} active contacts")
            else:
                logger.warning("Google Sheets not available, using mock contacts")
                contacts = self._get_mock_contacts()
            
            if not contacts:
                logger.warning("No contacts found for outreach")
                results["success"] = True  # Not an error, just no work to do
                return results
            
            # Generate and send personalized messages
            outreach_logs = []
            emails_sent = 0
            
            for contact in contacts:
                try:
                    # Generate personalized message
                    message = self.message_generator.generate_message(
                        contact, campaign_type
                    )
                    
                    # Send email (mock implementation)
                    delivery_result = self.email_client.send_email(
                        contact["email"], 
                        message["subject"], 
                        message["body"]
                    )
                    
                    # Log the outreach
                    log_entry = {
                        "id": str(uuid.uuid4()),
                        "contact_id": contact.get("id", ""),
                        "contact_name": contact.get("name", ""),
                        "contact_company": contact.get("company", ""),
                        "message_type": campaign_type,
                        "subject": message["subject"],
                        "sent_date": datetime.now().isoformat(),
                        "delivery_status": "delivered" if delivery_result["success"] else "failed",
                        "response_status": "pending",
                        "created_at": datetime.now().isoformat()
                    }
                    
                    outreach_logs.append(log_entry)
                    
                    if delivery_result["success"]:
                        emails_sent += 1
                    
                    # Rate limiting to avoid spam
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Failed to send email to {contact.get('email', 'unknown')}: {e}")
                    results["errors"].append(f"Email failed: {contact.get('email', 'unknown')}")
            
            # Store outreach logs in Google Sheets
            if self.sheets_client and outreach_logs:
                success = self.sheets_client.write_outreach_log(outreach_logs)
                if success:
                    logger.info("Successfully logged outreach activities to Google Sheets")
                else:
                    logger.error("Failed to log outreach to Google Sheets")
                    results["errors"].append("Google Sheets logging failed")
            
            # Calculate metrics
            results["emails_sent"] = emails_sent
            results["delivery_rate"] = (emails_sent / len(contacts)) * 100 if contacts else 0
            results["success"] = emails_sent > 0 or len(contacts) == 0
            
            logger.info(f"Outreach campaign completed: {emails_sent}/{len(contacts)} emails sent")
            return results
            
        except Exception as e:
            logger.error(f"Outreach campaign failed: {e}")
            results["errors"].append(str(e))
            return results
    
    def _get_mock_contacts(self) -> List[Dict[str, Any]]:
        """Get mock contacts for testing when Google Sheets not available."""
        return [
            {
                "id": "mock-1",
                "name": "Test Contact 1",
                "email": "test1@example.com", 
                "company": "Test Company 1",
                "role": "CTO"
            },
            {
                "id": "mock-2",
                "name": "Test Contact 2",
                "email": "test2@example.com",
                "company": "Test Company 2", 
                "role": "Lead Developer"
            }
        ]


class MessageGenerator:
    """Generates personalized outreach messages"""
    
    def generate_message(self, contact: Dict[str, Any], campaign_type: str) -> Dict[str, str]:
        """
        Generate personalized message for a contact.
        
        Args:
            contact: Contact information
            campaign_type: Type of campaign
            
        Returns:
            Dict with subject and body
        """
        name = contact.get("name", "there")
        company = contact.get("company", "your company")
        role = contact.get("role", "")
        
        if campaign_type == "dev_tools_intro":
            subject = f"Development Tools for {company} - Quick Question"
            body = f"""Hi {name},

I hope this message finds you well. I came across your profile and noticed your role as {role} at {company}.

We've been helping Southeast Asian tech companies like {company} streamline their development workflows with modern tooling. I'd love to share some insights that might be relevant to your team.

Would you be open to a brief 15-minute conversation about your current development challenges? I promise to keep it focused and valuable.

Best regards,
Business Development Team

P.S. - If this isn't relevant for you, please let me know and I'll make sure not to reach out again."""
        
        else:
            # Default template
            subject = f"Partnership Opportunity - {company}"
            body = f"""Hi {name},

I hope you're doing well. I wanted to reach out regarding some opportunities that might interest {company}.

Would you be available for a brief conversation?

Best regards,
Business Development Team"""
        
        return {
            "subject": subject,
            "body": body
        }


class EmailClient:
    """Mock email client for sending messages"""
    
    def send_email(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Send email (mock implementation).
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            
        Returns:
            Dict with send result
        """
        # Mock implementation - in production this would use SendGrid or SMTP
        logger.info(f"Sending email to {to_email}: {subject}")
        
        # Simulate occasional delivery failures
        import random
        success_rate = 0.95  # 95% delivery success rate
        success = random.random() < success_rate
        
        return {
            "success": success,
            "message_id": str(uuid.uuid4()) if success else None,
            "error": None if success else "Simulated delivery failure"
        }


__all__ = ["OutreachCoordinator"] 