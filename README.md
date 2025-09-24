# 🏠 Smart Yad2 Property Monitor

> **Simple, intelligent apartment finder for Yad2.co.il with anti-detection**

## 🎯 **What It Does**
- **Smart Monitoring**: Checks Yad2 every 7-13 minutes (randomized)
- **Database Storage**: Remembers what it's seen, no duplicates
- **Anti-Detection**: Random intervals, rotating headers, smart delays
- **New Property Alerts**: Email notifications for NEW apartments
- **Price Drop Alerts**: Get notified when prices are reduced! 💰
- **Market Updates**: Track when properties are sold/removed 📉
- **100% Free**: Configure with your own email service

## 🚀 **Quick Start**

### 1. Install
```bash
git clone https://github.com/maxko2/Yad2-Haifa-Monitor.git
cd Yad2-Haifa-Monitor
pip install -r requirements.txt
```

### 2. Setup Email Service
```bash
# Copy example environment file
copy .env.example .env

# Edit .env with your email credentials:
# EMAIL_ADDRESS=your-email@your-provider.com  
# EMAIL_PASSWORD=your-app-password
# RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com
```

### 3. Run
```bash
# Test everything works
python smart_yad2_main.py --test

# Run once manually  
python smart_yad2_main.py --once

# Start smart monitoring (randomized 7-13 min intervals)
python smart_yad2_main.py
```

## 📁 **Clean File Structure**
```
📁 Yad2-Sampling/
├── smart_yad2_main.py          # Main service
├── smart_yad2_sampler.py       # API handler with anti-detection
├── yad2_database.py            # SQLite database manager  
├── yad2_notification_manager.py # Email notifications
├── config.json                 # Search settings (Haifa, ₪5000 max)
├── run_smart_monitor.bat       # Windows scheduler setup
├── requirements.txt            # Dependencies
└── .env.example               # Environment template
```

## ⚙️ **Configuration**
Edit `config.json` to change search area/price:
```json
{
  "api_url": "https://www.yad2.co.il/realestate/_next/data/.../rent.json?maxPrice=5000&minRooms=2.5&maxRooms=5&topArea=25&area=5"
}
```

**Current Settings:**
- 📍 **Location**: Haifa and surrounding areas
- 💰 **Max Price**: Configurable (default ₪5,000/month)
- 🏠 **Rooms**: Configurable (default 2.5 - 5 rooms)
- 🎯 **Type**: Rental properties

## 🛡️ **Smart Features**
- **🏠 New Properties**: Instant email alerts for new listings
- **💰 Price Drops**: Get notified when rent prices are reduced  
- **📉 Market Updates**: Track when apartments are sold/removed
- **🎲 Anti-Detection**: Random intervals (7-13 min), rotating user-agents
- **💾 Smart Database**: Tracks all changes, no data loss
- **📧 Beautiful Emails**: HTML formatted with property photos

## 📊 **Database**
All data stored in `yad2_properties.db`:
- Properties table (all found apartments)  
- Monitoring runs table (statistics)
- Smart duplicate detection
- Persistent across restarts

## 🤝 **Commands**
```bash
python smart_yad2_main.py          # Start monitoring
python smart_yad2_main.py --once   # Single check
python smart_yad2_main.py --test   # Test all systems  
python smart_yad2_main.py --stats  # Show statistics
```

## 📝 **License**
MIT License - Use freely for personal apartment hunting!

---
**Made for finding apartments in Haifa and nearby areas** 🏠✨
