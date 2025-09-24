# Configuration Manager for GitHub Actions
import os
import json
from typing import Dict, Any

class GitHubConfig:
    """Configuration manager that works with GitHub Actions secrets."""
    
    def __init__(self):
        self.config_data = self._load_config()
        self._setup_from_environment()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load base configuration from config.json."""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except:
            return self._get_default_config()
    
    def _setup_from_environment(self):
        """Setup email configuration from environment variables."""
        # Support both Proton Mail and Gmail
        sender_email = os.getenv('PROTON_EMAIL') or os.getenv('GMAIL_EMAIL')
        sender_password = os.getenv('PROTON_PASSWORD') or os.getenv('GMAIL_APP_PASSWORD')
        recipient_emails = os.getenv('RECIPIENT_EMAILS') or os.getenv('RECIPIENT_EMAIL')
        
        if sender_email and sender_password:
            # Update email configuration with environment variables
            self.config_data['notifications']['email'].update({
                'enabled': True,
                'sender_email': sender_email,
                'sender_password': sender_password,
                'recipient_email': recipient_emails or sender_email
            })
            
            # Set SMTP settings based on provider
            if 'proton.me' in sender_email.lower():
                self.config_data['notifications']['email'].update({
                    'smtp_server': 'mail.proton.me',
                    'smtp_port': 587
                })
            else:
                self.config_data['notifications']['email'].update({
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587
                })
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for GitHub Actions."""
        return {
            "api": {
                "url": "https://www.yad2.co.il/realestate/_next/data/gtPYHLspEBp8Prnb6dWsk/rent.json?maxPrice=5000&minRooms=2.5&maxRooms=5&topArea=25&area=5",
                "method": "GET",
                "timeout": 30
            },
            "monitoring": {
                "check_interval_minutes": 10,
                "use_database": True,
                "random_user_agents": True
            },
            "notifications": {
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587
                },
                "sms": {
                    "enabled": False
                }
            }
        }
    
    def get(self, key: str, default=None):
        """Get configuration value using dot notation."""
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def is_email_enabled(self) -> bool:
        """Check if email notifications are enabled and configured."""
        email_config = self.config_data.get('notifications', {}).get('email', {})
        return (
            email_config.get('enabled', False) and
            email_config.get('sender_email') and
            email_config.get('sender_password')
        )
    
    def is_sms_enabled(self) -> bool:
        """SMS disabled for GitHub Actions by default."""
        return False
