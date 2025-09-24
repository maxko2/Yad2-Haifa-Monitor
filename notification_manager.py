import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os

class NotificationManager:
    """Base notification manager for email and SMS with Proton Mail support."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def send_email(self, subject: str, body: str, is_html: bool = False) -> bool:
        """Send email notification with Proton Mail support and multiple recipients."""
        try:
            # Get email configuration
            email_config = self.config.get('notifications.email', {})
            
            # Use environment variables if available (for GitHub Actions)
            sender_email = (os.getenv('PROTON_EMAIL') or os.getenv('GMAIL_EMAIL') or 
                          email_config.get('sender_email'))
            sender_password = (os.getenv('PROTON_PASSWORD') or os.getenv('GMAIL_APP_PASSWORD') or 
                             email_config.get('sender_password'))
            
            # Handle multiple recipients
            recipient_emails_str = (os.getenv('RECIPIENT_EMAILS') or os.getenv('RECIPIENT_EMAIL') or 
                                  email_config.get('recipient_email') or sender_email)
            
            # Parse multiple recipients (comma-separated)
            recipient_emails = [email.strip() for email in recipient_emails_str.split(',')]
            
            if not all([sender_email, sender_password]):
                self.logger.error("Email credentials not configured")
                return False
            
            # Determine SMTP settings based on email provider
            if 'proton.me' in sender_email.lower():
                smtp_server = 'mail.proton.me'
                smtp_port = 587
                self.logger.info("Using Proton Mail SMTP settings")
            elif 'gmail.com' in sender_email.lower():
                smtp_server = 'smtp.gmail.com'
                smtp_port = 587
                self.logger.info("Using Gmail SMTP settings")
            else:
                # Default to Gmail settings
                smtp_server = 'smtp.gmail.com'
                smtp_port = 587
                self.logger.info("Using default Gmail SMTP settings")
            
            # Send to each recipient
            success_count = 0
            for recipient_email in recipient_emails:
                try:
                    # Create message for each recipient
                    message = MIMEMultipart('alternative')
                    message['From'] = sender_email
                    message['To'] = recipient_email
                    message['Subject'] = subject
                    
                    # Add body
                    if is_html:
                        message.attach(MIMEText(body, 'html'))
                    else:
                        message.attach(MIMEText(body, 'plain'))
                    
                    # Send email
                    with smtplib.SMTP(smtp_server, smtp_port) as server:
                        server.starttls()
                        server.login(sender_email, sender_password)
                        server.send_message(message)
                    
                    self.logger.info(f"Email sent successfully to {recipient_email}")
                    success_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Failed to send email to {recipient_email}: {e}")
            
            self.logger.info(f"Email notifications: {success_count}/{len(recipient_emails)} sent successfully")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def send_sms(self, message: str) -> bool:
        """Send SMS notification (disabled by default)."""
        self.logger.info("SMS notifications not configured")
        return False
