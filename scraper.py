import requests
from bs4 import BeautifulSoup
import pymongo
from datetime import datetime, timedelta
import math

client = pymongo.MongoClient("mongodb://localhost:27017/")
online_db = client['online_vendor_db']
offline_db = client['offline_vendor_db']
online_collection = online_db['vendors']
offline_collection = offline_db['vendors']

# Check if the offline collection exists, and create it if it does not
if 'offline_vendor_db' not in client.list_database_names():
    offline_db = client['offline_vendor_db']
if 'vendors' not in offline_db.list_collection_names():
    offline_collection = offline_db['vendors']
    # Example data insertion for the offline collection
    offline_data = [
        {"vendor": "MK Digital Stores", "mobile_name": "iPhone 13", "price": 69999, "rating": 4.5, "distance": 2.5, "latitude": 28.6139, "longitude": 77.2090, "delivery_days": 5},
        {"vendor": "MK Digital Stores", "mobile_name": "iPhone 14", "price": 79999, "rating": 4.7, "distance": 2.5, "latitude": 28.6139, "longitude": 77.2090, "delivery_days": 5},
        {"vendor": "SSI Stores", "mobile_name": "iPhone 13", "price": 69999, "rating": 4.6, "distance": 3.0, "latitude": 28.7041, "longitude": 77.1025, "delivery_days": 6},
        {"vendor": "SSI Stores", "mobile_name": "iPhone 14", "price": 79999, "rating": 4.8, "distance": 3.0, "latitude": 28.7041, "longitude": 77.1025, "delivery_days": 6},
    ]
    offline_collection.insert_many(offline_data)

# Web scraping functions (Amazon, Flipkart, etc.)
def scrape_amazon(mobile_name):
    # Dummy data for the sake of example
    return {"vendor": "Amazon", "price": 11500, "rating": 4.6, "delivery_days": 3, "buy_link": "http://example.com"}

def scrape_flipkart(mobile_name):
    # Dummy data for the sake of example
    return {"vendor": "Flipkart", "price": 10500, "rating": 4.6, "delivery_days": 2, "buy_link": "http://example.com"}

# Add similar functions for Reliance Digital, Croma, Poorvika, and Supreme Mobiles

def get_vendor_data(mobile_name):
    data = []
    data.append(scrape_amazon(mobile_name))
    data.append(scrape_flipkart(mobile_name))
    # Append data from other vendors
    return data

def update_online_database(mobile_name):
    vendor_data = get_vendor_data(mobile_name)
    timestamp = datetime.now()
    for data in vendor_data:
        data['mobile_name'] = mobile_name
        data['timestamp'] = timestamp
        online_collection.insert_one(data)

def get_online_data_from_db(mobile_name):
    data = list(online_collection.find({"mobile_name": mobile_name}))
    if not data:
        update_online_database(mobile_name)
        data = list(online_collection.find({"mobile_name": mobile_name}))
    else:
        latest_entry = max(data, key=lambda x: x['timestamp'])
        if datetime.now() - latest_entry['timestamp'] > timedelta(days=1):
            online_collection.delete_many({"mobile_name": mobile_name})
            update_online_database(mobile_name)
            data = list(online_collection.find({"mobile_name": mobile_name}))
    return data

def get_offline_data_from_db(mobile_name):
    data = list(offline_collection.find({"mobile_name": mobile_name}))
    return data

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) * math.sin(d_lat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) * math.sin(d_lon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance
