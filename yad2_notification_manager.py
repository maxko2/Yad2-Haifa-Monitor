import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def send_property_notifications(new_properties: List[Dict[str, Any]], 
                               price_changes: List[Dict[str, Any]], 
                               recipients: List[str]):
    """Send email notifications for new properties and price changes."""
    
    if not new_properties and not price_changes:
        logger.info("No properties to notify about")
        return
    
    # Get Gmail credentials from environment
    gmail_user = os.getenv('GMAIL_EMAIL')
    gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    
    if not gmail_user or not gmail_password:
        logger.error("Gmail credentials not found in environment variables")
        return
    
    try:
        # Create email content
        subject = f"🏠 Yad2 Haifa Update: {len(new_properties)} New + {len(price_changes)} Price Changes"
        html_body = create_email_html(new_properties, price_changes)
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = gmail_user
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        # Add HTML body
        html_part = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {len(recipients)} recipients")
        
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise

def create_email_html(new_properties: List[Dict[str, Any]], 
                     price_changes: List[Dict[str, Any]]) -> str:
    """Create HTML email content for property notifications."""
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            .property { border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 8px; }
            .new { background-color: #e8f8f5; border-left: 5px solid #27ae60; }
            .price-change { background-color: #fef9e7; border-left: 5px solid #f39c12; }
            .good-deal { background-color: #ebf3fd; border-left: 5px solid #3498db; }
            .price { font-size: 20px; font-weight: bold; color: #27ae60; }
            .title { font-size: 16px; font-weight: bold; margin-bottom: 8px; }
            .details { color: #555; margin: 5px 0; }
            .amenities { font-style: italic; color: #777; }
            .contact { background-color: #f8f9fa; padding: 8px; border-radius: 4px; margin-top: 10px; }
        </style>
    </head>
    <body>
    """
    
    html += f"""
        <div class="header">
            <h1>🏠 Yad2 Haifa Property Monitor</h1>
            <p>Update from {new_properties[0]['first_seen'][:10] if new_properties else price_changes[0]['change_date'][:10]}</p>
        </div>
    """
    
    # New properties section
    if new_properties:
        html += f"""
        <h2>✨ {len(new_properties)} New Properties</h2>
        """
        
        # Limit to first 10 properties to avoid huge emails
        for prop in new_properties[:10]:
            price = int(prop.get('price', 0))
            is_good_deal = price <= 4000
            
            css_class = "property new"
            if is_good_deal:
                css_class += " good-deal"
            
            html += f"""
            <div class="{css_class}">
                <div class="title">{prop.get('title', 'No title')}</div>
                <div class="price">₪{price:,}</div>
                <div class="details">
                    📍 {prop.get('address', 'No address')} - {prop.get('neighborhood', '')}
                </div>
                <div class="details">
                    🏠 {prop.get('rooms', 0)} rooms • 📐 {prop.get('size', 0)}m² • 🏢 Floor {prop.get('floor', 'N/A')}
                </div>
            """
            
            if prop.get('amenities'):
                amenities = ', '.join([a for a in prop['amenities'][:3] if a])  # First 3 amenities
                if amenities:
                    html += f'<div class="amenities">✨ {amenities}</div>'
            
            if prop.get('contact_name') or prop.get('phone'):
                html += f"""
                <div class="contact">
                    📞 {prop.get('contact_name', 'Contact')}: {prop.get('phone', 'No phone')}
                </div>
                """
            
            html += "</div>"
        
        if len(new_properties) > 10:
            html += f"<p><i>... and {len(new_properties) - 10} more new properties</i></p>"
    
    # Price changes section
    if price_changes:
        html += f"""
        <h2>💰 {len(price_changes)} Price Changes</h2>
        """
        
        for change in price_changes[:5]:  # Show first 5 price changes
            old_price = int(change.get('old_price', 0))
            new_price = int(change.get('new_price', 0))
            change_amount = new_price - old_price
            change_direction = "📈" if change_amount > 0 else "📉"
            
            html += f"""
            <div class="property price-change">
                <div class="title">{change.get('title', 'No title')}</div>
                <div class="price">
                    ₪{old_price:,} → ₪{new_price:,} ({change_direction} {change_amount:+,})
                </div>
                <div class="details">
                    📍 {change.get('address', 'No address')}
                </div>
            </div>
            """
    
    html += """
        <hr style="margin: 30px 0;">
        <p style="color: #888; font-size: 12px;">
            This is an automated notification from Yad2 Haifa Property Monitor.<br>
            Running every 10 minutes via GitHub Actions to find you the best rentals! 🏠✨
        </p>
    </body>
    </html>
    """
    
    return html