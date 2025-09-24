import requests
import json
import random
import time

def test_api_response():
    """Test the API response structure"""
    
    # Create session with advanced settings
    session = requests.Session()
    
    # Realistic user agent
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    ]
    
    selected_ua = random.choice(user_agents)
    
    # Build realistic headers
    headers = {
        'User-Agent': selected_ua,
        'Accept': '*/*',
        'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.yad2.co.il/',
        'Origin': 'https://www.yad2.co.il',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors', 
        'Sec-Fetch-Site': 'same-origin',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'DNT': '1',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    session.headers.update(headers)
    
    # Add common cookies that browsers have
    session.cookies.update({
        'lang': 'he',
        'currency': 'NIS',
    })
    
    try:
        # Visit main page first
        print("🤖 Simulating human browsing behavior...")
        main_response = session.get('https://www.yad2.co.il/', timeout=10)
        print(f"📄 Visited main page: {main_response.status_code}")
        time.sleep(random.uniform(2, 4))
        
        # Visit real estate section
        realestate_response = session.get('https://www.yad2.co.il/realestate/rent', timeout=10)
        print(f"🏠 Visited realestate section: {realestate_response.status_code}")
        time.sleep(random.uniform(3, 6))
        
        # API request
        api_url = "https://www.yad2.co.il/realestate/_next/data/gtPYHLspEBp8Prnb6dWsk/rent.json"
        params = {
            'maxPrice': '5000',
            'minRooms': '2.5',
            'maxRooms': '5',
            'topArea': '25',
            'area': '5'
        }
        
        api_headers = session.headers.copy()
        api_headers.update({
            'Accept': 'application/json',
            'x-nextjs-data': '1',
            'Referer': 'https://www.yad2.co.il/realestate/rent'
        })
        
        print("🔍 Making API request...")
        response = session.get(api_url, params=params, headers=api_headers, timeout=30)
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📄 Content-Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Successfully parsed JSON response!")
                
                # Analyze structure
                print("\n📊 Response structure analysis:")
                print(f"Top-level keys: {list(data.keys())}")
                
                if 'pageProps' in data:
                    print(f"pageProps keys: {list(data['pageProps'].keys())}")
                    
                    if 'searchResults' in data['pageProps']:
                        search_results = data['pageProps']['searchResults']
                        print(f"searchResults keys: {list(search_results.keys())}")
                        
                        if 'feed' in search_results:
                            feed = search_results['feed']
                            print(f"feed keys: {list(feed.keys())}")
                            
                            if 'feed_items' in feed:
                                feed_items = feed['feed_items']
                                print(f"Found {len(feed_items)} feed items")
                                
                                # Check first few items
                                for i, item in enumerate(feed_items[:3]):
                                    print(f"Item {i+1} keys: {list(item.keys())}")
                                    print(f"Item {i+1} type: {item.get('type', 'unknown')}")
                
                # Save sample for debugging
                with open('api_response_sample.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print("\n💾 Saved response sample to 'api_response_sample.json'")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"Response preview: {response.text[:500]}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_response()
