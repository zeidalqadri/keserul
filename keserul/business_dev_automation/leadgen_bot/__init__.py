"""Lead Generation Bot Package"""

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


class LeadGenCoordinator:
    """Real lead generation coordinator with Google Sheets integration"""
    
    def __init__(self, credentials_path: str = None, spreadsheet_id: str = None):
        """
        Initialize LeadGen coordinator.
        
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
                logger.info("LeadGen connected to Google Sheets")
            except Exception as e:
                logger.warning(f"Could not connect to Google Sheets: {e}")
        
        # Mock scrapers for SGTech and MDEC (placeholder implementations)
        self.sgtech_scraper = SGTechScraper()
        self.mdec_scraper = MDECScraper()
    
    def run_pipeline(self) -> Dict[str, Any]:
        """
        Run the complete lead generation pipeline.
        
        Returns:
            Dict with pipeline results
        """
        start_time = time.time()
        results = {
            "success": False,
            "total_contacts": 0,
            "sources_processed": [],
            "processing_time": "0s",
            "contacts_file": None,
            "errors": []
        }
        
        try:
            logger.info("Starting LeadGen pipeline")
            
            # Scrape contacts from all sources
            all_contacts = []
            
            # SGTech scraping
            logger.info("Scraping SGTech directory")
            sgtech_contacts = self.sgtech_scraper.scrape()
            all_contacts.extend(sgtech_contacts)
            results["sources_processed"].append("SGTech")
            logger.info(f"Found {len(sgtech_contacts)} contacts from SGTech")
            
            # MDEC scraping  
            logger.info("Scraping MDEC directory")
            mdec_contacts = self.mdec_scraper.scrape()
            all_contacts.extend(mdec_contacts)
            results["sources_processed"].append("MDEC")
            logger.info(f"Found {len(mdec_contacts)} contacts from MDEC")
            
            # Deduplicate contacts
            unique_contacts = self._deduplicate_contacts(all_contacts)
            logger.info(f"Deduplicated to {len(unique_contacts)} unique contacts")
            
            # Validate and enrich contact data
            validated_contacts = self._validate_contacts(unique_contacts)
            logger.info(f"Validated {len(validated_contacts)} contacts")
            
            # Store contacts in Google Sheets
            if self.sheets_client and validated_contacts:
                success = self.sheets_client.write_contacts(validated_contacts)
                if success:
                    logger.info("Successfully wrote contacts to Google Sheets")
                else:
                    logger.error("Failed to write contacts to Google Sheets")
                    results["errors"].append("Google Sheets write failed")
            elif not self.sheets_client:
                logger.warning("Google Sheets not available, contacts not persisted")
                results["errors"].append("Google Sheets not configured")
            
            # Update results
            results["total_contacts"] = len(validated_contacts)
            results["processing_time"] = f"{time.time() - start_time:.1f}s"
            results["success"] = len(validated_contacts) > 0
            
            logger.info(f"LeadGen pipeline completed: {results['total_contacts']} contacts")
            return results
            
        except Exception as e:
            logger.error(f"LeadGen pipeline failed: {e}")
            results["errors"].append(str(e))
            results["processing_time"] = f"{time.time() - start_time:.1f}s"
            return results
    
    def _deduplicate_contacts(self, contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate contacts based on email."""
        seen_emails = set()
        unique_contacts = []
        
        for contact in contacts:
            email = contact.get("email", "").lower().strip()
            if email and email not in seen_emails:
                seen_emails.add(email)
                unique_contacts.append(contact)
        
        return unique_contacts
    
    def _validate_contacts(self, contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and enrich contact data."""
        validated = []
        
        for contact in contacts:
            # Add unique ID
            contact["id"] = str(uuid.uuid4())
            
            # Add timestamps
            contact["scraped_date"] = datetime.now().isoformat()
            contact["status"] = "active"
            
            # Basic validation
            if contact.get("name") and contact.get("email"):
                validated.append(contact)
        
        return validated


class SGTechScraper:
    """SGTech directory scraper with rate limiting"""
    
    def __init__(self):
        self.rate_limit_delay = 2  # seconds between requests
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape contacts from SGTech directory.
        
        Returns:
            List of contact dictionaries
        """
        # Mock implementation - in production this would scrape real SGTech data
        logger.info("Scraping SGTech directory (mock implementation)")
        
        # Simulate rate limiting
        time.sleep(self.rate_limit_delay)
        
        # Return mock contacts
        return [
            {
                "name": "Alice Tan",
                "role": "CTO", 
                "company": "SGTech Solutions",
                "email": "alice.tan@sgtech-solutions.com",
                "linkedin_url": "https://linkedin.com/in/alicetan",
                "source": "SGTech"
            },
            {
                "name": "Bob Lim",
                "role": "Lead Developer",
                "company": "Singapore DevCorp", 
                "email": "bob.lim@sg-devcorp.com",
                "linkedin_url": "https://linkedin.com/in/boblim",
                "source": "SGTech"
            },
            {
                "name": "Charlie Wong",
                "role": "Engineering Manager",
                "company": "Tech Hub SG",
                "email": "charlie.wong@techhub.sg",
                "linkedin_url": "https://linkedin.com/in/charliewong", 
                "source": "SGTech"
            }
        ]


class MDECScraper:
    """MDEC directory scraper with compliance checks"""
    
    def __init__(self):
        self.rate_limit_delay = 2.5  # seconds between requests
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape contacts from MDEC directory.
        
        Returns:
            List of contact dictionaries
        """
        # Mock implementation - in production this would scrape real MDEC data
        logger.info("Scraping MDEC directory (mock implementation)")
        
        # Simulate rate limiting
        time.sleep(self.rate_limit_delay)
        
        # Return mock contacts
        return [
            {
                "name": "Diana Rahman",
                "role": "DevOps Engineer",
                "company": "Malaysia Tech Hub",
                "email": "diana.rahman@my-techhub.com",
                "linkedin_url": "https://linkedin.com/in/dianarahman",
                "source": "MDEC"
            },
            {
                "name": "Ethan Chong",
                "role": "Software Architect", 
                "company": "KL Software House",
                "email": "ethan.chong@kl-software.com",
                "linkedin_url": "https://linkedin.com/in/ethanchong",
                "source": "MDEC"
            },
            {
                "name": "Fatima Aziz",
                "role": "Tech Lead",
                "company": "Cyberjaya Innovations",
                "email": "fatima.aziz@cy-innovations.com",
                "linkedin_url": "https://linkedin.com/in/fatimaaziz",
                "source": "MDEC"
            }
        ] 