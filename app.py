from flask import Flask, request, render_template
from model_inference import *
from scraper import get_online_data_from_db, get_offline_data_from_db, calculate_distance
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/result', methods=['POST'])
def result():
    query = request.form['query']
    filter_location = 'filter_location' in request.form
    user_lat = float(request.form.get('latitude', 0.0)) if filter_location else None
    user_lon = float(request.form.get('longitude', 0.0)) if filter_location else None
    
    predicted_label, mobile_name = predict_and_extract(query, model, tokenizer, products)
    
    category_sort = None
    if mobile_name:
        online_vendor_data = get_online_data_from_db(mobile_name)
        offline_vendor_data = get_offline_data_from_db(mobile_name)

        # Calculate distance for offline vendors and filter based on distance if user location is provided
        if user_lat and user_lon:
            for vendor in offline_vendor_data:
                vendor['distance'] = calculate_distance(user_lat, user_lon, vendor['latitude'], vendor['longitude'])
            offline_vendor_data = sorted(offline_vendor_data, key=lambda x: x['distance']) 

        if predicted_label == 0:  # Cheapest
            category_sort = "Cheapest"
            online_vendor_data = sorted(online_vendor_data, key=lambda x: x['price'])
            offline_vendor_data = sorted(offline_vendor_data, key=lambda x: x['price'])
           
        elif predicted_label == 1:  # Fastest Delivery
            category_sort = "Fastest Delivery"
            online_vendor_data = sorted(online_vendor_data, key=lambda x: x['delivery_days'])
            offline_vendor_data = sorted(offline_vendor_data, key=lambda x: x['delivery_days'])
        elif predicted_label == 2:  # Best Overall
            category_sort = "Best Overall"
            online_vendor_data = sorted(online_vendor_data, key=lambda x: (x['price'], x['delivery_days'], -x['rating']))
            offline_vendor_data = sorted(offline_vendor_data, key=lambda x: (x['price'], x['delivery_days'], -x['rating']))
        elif predicted_label == 3:  # Best Warranty
            category_sort = "Best Warranty"
            online_vendor_data = sorted(online_vendor_data, key=lambda x: x['warranty'])  # Assuming warranty field exists
            offline_vendor_data = sorted(offline_vendor_data, key=lambda x: x['warranty'])
        elif predicted_label == 4:  # Highest Rated
            category_sort = "Highest Rated"
            online_vendor_data = sorted(online_vendor_data, key=lambda x: -x['rating'])
            offline_vendor_data = sorted(offline_vendor_data, key=lambda x: -x['rating'])

        
    else:
        return render_template('result.html', error="No mobile name mentioned in the query.")
    
    return render_template('result.html', 
                           online_vendors=online_vendor_data, 
                           offline_vendors=offline_vendor_data, 
                           mobile_name=mobile_name,
                           category_sort=category_sort,
                           lat = user_lat,
                           lon = user_lon)

if __name__ == '__main__':
    app.run(debug=True)
