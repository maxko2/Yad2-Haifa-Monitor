from notification_manager import NotificationManager
from typing import List, Dict, Any
import logging
from datetime import datetime

class Yad2NotificationManager(NotificationManager):
    """Specialized notification manager for Yad2 properties."""
    
    def format_property_message(self, properties: List[Dict[str, Any]]) -> str:
        """
        Format Yad2 properties into a readable message.
        
        Args:
            properties: List of Yad2 property data
            
        Returns:
            Formatted message string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not properties:
            return f"🏠 Yad2 Monitor Alert - {timestamp}\n\nData changed but no new properties found."
        
        message = f"🏠 Yad2 New Properties Alert - {timestamp}\n\n"
        message += f"Found {len(properties)} new rental propert{'ies' if len(properties) != 1 else 'y'}:\n\n"
        
        for i, prop in enumerate(properties[:5], 1):  # Limit to first 5 properties
            message += f"🏡 Property #{i}:\n"
            
            # Price
            price = prop.get('price', 'N/A')
            if price != 'N/A':
                message += f"💰 Price: ₪{price:,}/month\n"
            else:
                message += f"💰 Price: {price}\n"
            
            # Address
            address = prop.get('address', 'N/A')
            message += f"📍 Address: {address}\n"
            
            # Property details
            rooms = prop.get('rooms', 'N/A')
            size = prop.get('size_sqm', 'N/A')
            floor = prop.get('floor', 'N/A')
            
            details = []
            if rooms != 'N/A':
                details.append(f"{rooms} rooms")
            if size != 'N/A':
                details.append(f"{size}m²")
            if floor != 'N/A':
                details.append(f"Floor {floor}")
            
            if details:
                message += f"🏠 Details: {', '.join(details)}\n"
            
            # Property type and condition
            prop_type = prop.get('property_type', 'N/A')
            condition = prop.get('condition', 'N/A')
            
            if prop_type != 'N/A' or condition != 'N/A':
                extra_info = []
                if prop_type != 'N/A':
                    extra_info.append(prop_type)
                if condition != 'N/A':
                    extra_info.append(condition)
                message += f"ℹ️  Type: {', '.join(extra_info)}\n"
            
            # URL
            url = prop.get('url', '')
            if url:
                message += f"🔗 View: {url}\n"
            
            message += "\n"
        
        if len(properties) > 5:
            message += f"... and {len(properties) - 5} more properties!\n\n"
        
        message += "Happy apartment hunting! 🏠✨"
        
        return message
    
    def format_property_html(self, properties: List[Dict[str, Any]]) -> str:
        """
        Format Yad2 properties into HTML email content.
        
        Args:
            properties: List of Yad2 property data
            
        Returns:
            HTML formatted message
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .timestamp {{ margin-top: 5px; opacity: 0.9; font-size: 14px; }}
                .content {{ padding: 20px; }}
                .summary {{ background-color: #e8f4f8; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; }}
                .property {{ border: 2px solid #e0e0e0; margin: 15px 0; border-radius: 10px; overflow: hidden; }}
                .property-header {{ background-color: #f8f9fa; padding: 15px; border-bottom: 1px solid #e0e0e0; }}
                .property-title {{ font-weight: bold; font-size: 18px; color: #2c3e50; margin: 0; }}
                .price {{ color: #e74c3c; font-size: 20px; font-weight: bold; }}
                .property-body {{ padding: 15px; }}
                .property-detail {{ margin: 8px 0; display: flex; align-items: center; }}
                .icon {{ width: 20px; margin-right: 8px; }}
                .address {{ color: #7f8c8d; font-style: italic; }}
                .details {{ background-color: #f1f8ff; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .view-button {{ display: inline-block; background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px; }}
                .view-button:hover {{ background-color: #2980b9; }}
                .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; color: #7f8c8d; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏠 Yad2 New Properties Alert</h1>
                    <div class="timestamp">{timestamp}</div>
                </div>
                
                <div class="content">
                    <div class="summary">
                        <h2 style="margin: 0; color: #2c3e50;">🎉 {len(properties)} New Rental Propert{'ies' if len(properties) != 1 else 'y'} Found!</h2>
                        <p style="margin: 10px 0 0 0;">Matching your search criteria</p>
                    </div>
        """
        
        for i, prop in enumerate(properties[:10], 1):  # Show up to 10 properties
            price = prop.get('price', 'N/A')
            address = prop.get('address', 'N/A')
            rooms = prop.get('rooms', 'N/A')
            size = prop.get('size_sqm', 'N/A')
            floor = prop.get('floor', 'N/A')
            prop_type = prop.get('property_type', 'N/A')
            condition = prop.get('condition', 'N/A')
            url = prop.get('url', '')
            
            price_display = f"₪{price:,}/month" if price != 'N/A' else 'Price not specified'
            
            html += f"""
            <div class="property">
                <div class="property-header">
                    <div class="property-title">Property #{i}</div>
                    <div class="price">{price_display}</div>
                </div>
                <div class="property-body">
                    <div class="property-detail">
                        <span class="icon">📍</span>
                        <span class="address">{address}</span>
                    </div>
            """
            
            # Property details
            details = []
            if rooms != 'N/A':
                details.append(f"{rooms} rooms")
            if size != 'N/A':
                details.append(f"{size}m²")
            if floor != 'N/A':
                details.append(f"Floor {floor}")
            
            if details:
                html += f"""
                    <div class="details">
                        <strong>🏠 Property Details:</strong> {' • '.join(details)}
                    </div>
                """
            
            # Type and condition
            if prop_type != 'N/A' or condition != 'N/A':
                extra_info = []
                if prop_type != 'N/A':
                    extra_info.append(prop_type)
                if condition != 'N/A':
                    extra_info.append(condition)
                
                html += f"""
                    <div class="property-detail">
                        <span class="icon">ℹ️</span>
                        <span>{' • '.join(extra_info)}</span>
                    </div>
                """
            
            # View button
            if url:
                html += f"""
                    <a href="{url}" class="view-button" target="_blank">View Property on Yad2</a>
                """
            
            html += """
                </div>
            </div>
            """
        
        if len(properties) > 10:
            html += f"""
            <div class="summary">
                <p><strong>... and {len(properties) - 10} more properties!</strong></p>
                <p>Check your Yad2 search for all results.</p>
            </div>
            """
        
        html += """
                </div>
                <div class="footer">
                    <p>Happy apartment hunting! 🏠✨</p>
                    <p><em>This alert was generated by your Yad2 API Monitor</em></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_yad2_notification(self, new_properties: List[Dict[str, Any]]) -> Dict[str, bool]:
        """
        Send Yad2-specific notifications.
        
        Args:
            new_properties: List of new Yad2 properties
            
        Returns:
            Dict with success status for each notification type
        """
        results = {'email': False, 'sms': False}
        
        if not new_properties:
            return results
        
        # Send email notification
        if self.config.is_email_enabled():
            subject = f"🏠 Yad2 Alert: {len(new_properties)} New Rental{'s' if len(new_properties) != 1 else ''} Found!"
            
            html_message = self.format_property_html(new_properties)
            results['email'] = self.send_email(subject, html_message, is_html=True)
        
        # Send SMS notification
        if self.config.is_sms_enabled():
            # SMS message should be concise
            if len(new_properties) == 1:
                prop = new_properties[0]
                price = prop.get('price', 'N/A')
                address_parts = prop.get('address', '').split(', ')
                area = address_parts[0] if address_parts else 'Unknown area'
                
                price_text = f"₪{price:,}" if price != 'N/A' else 'Price TBD'
                sms_message = f"🏠 New Yad2 rental: {price_text}/mo in {area}. Check your email for details!"
            else:
                sms_message = f"🏠 Yad2 Alert: {len(new_properties)} new rentals found! Check your email for full details."
            
            results['sms'] = self.send_sms(sms_message)
        
        return results

    def send_price_change_notification(self, price_changes: List[Dict[str, Any]]) -> Dict[str, bool]:
        """
        Send notifications about price changes.
        
        Args:
            price_changes: List of price change data
            
        Returns:
            Dict with success status for each notification type
        """
        results = {'email': False, 'sms': False}
        
        if not price_changes:
            return results
        
        # Filter for price reductions (interesting ones)
        price_drops = [pc for pc in price_changes if pc.get('price_diff', 0) < 0]
        
        if not price_drops:
            return results
        
        # Send email notification
        if self.config.is_email_enabled():
            subject = f"💰 Yad2 Price Drop Alert: {len(price_drops)} Property Price{'s' if len(price_drops) != 1 else ''} Reduced!"
            
            html_message = self._format_price_changes_html(price_drops)
            results['email'] = self.send_email(subject, html_message, is_html=True)
        
        # Send SMS notification
        if self.config.is_sms_enabled():
            if len(price_drops) == 1:
                pc = price_drops[0]
                address_parts = pc.get('address', '').split(', ')
                area = address_parts[0] if address_parts else 'Property'
                diff = abs(pc.get('price_diff', 0))
                sms_message = f"💰 Price drop! {area} reduced by ₪{diff:,}/mo. New price: ₪{pc.get('new_price', 0):,}"
            else:
                total_savings = sum(abs(pc.get('price_diff', 0)) for pc in price_drops)
                sms_message = f"💰 {len(price_drops)} price drops! Total savings up to ₪{total_savings:,}/mo. Check email!"
            
            results['sms'] = self.send_sms(sms_message)
        
        return results

    def send_removed_properties_notification(self, removed_properties: List[Dict[str, Any]]) -> Dict[str, bool]:
        """
        Send notifications about removed/sold properties.
        
        Args:
            removed_properties: List of removed property data
            
        Returns:
            Dict with success status for each notification type
        """
        results = {'email': False, 'sms': False}
        
        if not removed_properties or len(removed_properties) < 5:  # Only notify if significant number removed
            return results
        
        # Send email notification only (SMS would be too frequent)
        if self.config.is_email_enabled():
            subject = f"📉 Yad2 Market Update: {len(removed_properties)} Properties No Longer Available"
            
            html_message = self._format_removed_properties_html(removed_properties)
            results['email'] = self.send_email(subject, html_message, is_html=True)
        
        return results

    def _format_price_changes_html(self, price_changes: List[Dict[str, Any]]) -> str:
        """Format price changes into HTML email content."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #4CAF50, #45a049); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .price-change {{ background-color: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #4CAF50; }}
                .price-drop {{ color: #4CAF50; font-weight: bold; font-size: 1.2em; }}
                .old-price {{ text-decoration: line-through; color: #666; }}
                .new-price {{ color: #4CAF50; font-weight: bold; }}
                .address {{ font-size: 1.1em; margin-bottom: 10px; color: #333; }}
                .savings {{ background-color: #4CAF50; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💰 Yad2 Price Drop Alert!</h1>
                    <p>{timestamp}</p>
                </div>
                <div class="content">
                    <h2>🎉 Great News! Property Prices Have Dropped!</h2>
                    <p>We found <strong>{len(price_changes)}</strong> propert{'ies' if len(price_changes) != 1 else 'y'} with reduced prices:</p>
        """
        
        for pc in price_changes[:10]:  # Limit to 10
            address = pc.get('address', 'Unknown address')
            old_price = pc.get('old_price', 0)
            new_price = pc.get('new_price', 0)
            savings = abs(pc.get('price_diff', 0))
            
            html += f"""
                    <div class="price-change">
                        <div class="address">📍 {address}</div>
                        <div class="price-drop">
                            Price: <span class="old-price">₪{old_price:,}/mo</span> → <span class="new-price">₪{new_price:,}/mo</span>
                        </div>
                        <div style="margin-top: 10px;">
                            <span class="savings">💰 Save ₪{savings:,}/month!</span>
                        </div>
                    </div>
            """
        
        if len(price_changes) > 10:
            html += f"<p><strong>... and {len(price_changes) - 10} more price drops!</strong></p>"
        
        total_savings = sum(abs(pc.get('price_diff', 0)) for pc in price_changes)
        html += f"""
                    <div style="background-color: #e8f5e8; padding: 20px; border-radius: 8px; margin-top: 20px; text-align: center;">
                        <h3>💸 Total Potential Monthly Savings: ₪{total_savings:,}</h3>
                        <p>Act fast - these deals might not last long!</p>
                    </div>
                </div>
                <div style="text-align: center; padding: 20px; color: #666;">
                    <p>Happy apartment hunting! 🏠✨</p>
                    <p><em>This alert was generated by your Smart Yad2 Monitor</em></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

    def _format_removed_properties_html(self, removed_properties: List[Dict[str, Any]]) -> str:
        """Format removed properties into HTML email content."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #ff6b35, #f7931e); color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .removed-property {{ background-color: #fff3cd; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #ffc107; }}
                .summary {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📉 Market Update</h1>
                    <p>{timestamp}</p>
                </div>
                <div class="content">
                    <h2>Properties No Longer Available</h2>
                    <p><strong>{len(removed_properties)}</strong> properties were removed from the market (likely sold or rented):</p>
        """
        
        for prop in removed_properties[:15]:  # Show up to 15
            address = prop.get('address', 'Unknown address')
            price = prop.get('price', 0)
            
            html += f"""
                    <div class="removed-property">
                        📍 {address} - ₪{price:,}/month
                    </div>
            """
        
        if len(removed_properties) > 15:
            html += f"<p><em>... and {len(removed_properties) - 15} more properties</em></p>"
        
        html += f"""
                    <div class="summary">
                        <h3>📊 Market Insight</h3>
                        <p>The rental market is active! These properties were likely snapped up quickly.</p>
                        <p>Keep monitoring for new opportunities!</p>
                    </div>
                </div>
                <div style="text-align: center; padding: 20px; color: #666;">
                    <p>Stay alert for new listings! 🏠✨</p>
                    <p><em>This update was generated by your Smart Yad2 Monitor</em></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
