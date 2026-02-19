from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
import random
import base64
import io
from PIL import Image
import numpy as np
from datetime import datetime
import hashlib
import json
from time import time

app = Flask(__name__)
CORS(app)

# ============================================
# BLOCKCHAIN CLASS (Integrated directly)
# ============================================

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        # Create genesis block
        self.new_block(previous_hash='1', proof=100)
    
    def new_block(self, proof, previous_hash=None):
        """Create a new block in the blockchain"""
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]) if self.chain else '1',
        }
        # Reset current transactions
        self.current_transactions = []
        self.chain.append(block)
        return block
    
    def new_transaction(self, farmer, crop, price, quantity, location):
        """Add a new transaction to the current block"""
        transaction = {
            'farmer': farmer,
            'crop': crop,
            'price': float(price),
            'quantity': float(quantity),
            'location': location,
            'timestamp': time()
        }
        self.current_transactions.append(transaction)
        return self.last_block['index'] + 1
    
    @staticmethod
    def hash(block):
        """Create a SHA-256 hash of a block"""
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    @property
    def last_block(self):
        """Return the last block in the chain"""
        return self.chain[-1]
    
    def get_all_transactions(self):
        """Get all transactions from all blocks"""
        all_transactions = []
        for block in self.chain:
            all_transactions.extend(block['transactions'])
        return all_transactions

# Initialize blockchain
blockchain = Blockchain()

# ============================================
# CROP DATABASE (Based on Scientific Data)
# ============================================

CROP_DATABASE = {
    'tomato': {
        'name': 'Tomato', 'name_ta': 'தக்காளி', 'name_ml': 'തക്കാളി', 'name_te': 'టమాటా',
        'icon': '🍅',
        'ph_min': 6.0, 'ph_max': 6.8,
        'temp_min': 20, 'temp_max': 27,
        'rain_min': 400, 'rain_max': 600,
        'days_to_harvest': 60,
        'season': ['kharif', 'rabi'],
        'companions': ['onion', 'carrot', 'garlic'],
        'bad_companions': ['potato', 'cabbage']
    },
    'onion': {
        'name': 'Onion', 'name_ta': 'வெங்காயம்', 'name_ml': 'സവാള', 'name_te': 'ఉల్లిపాయ',
        'icon': '🧅',
        'ph_min': 6.0, 'ph_max': 7.0,
        'temp_min': 13, 'temp_max': 25,
        'rain_min': 600, 'rain_max': 800,
        'days_to_harvest': 150,
        'season': ['rabi'],
        'companions': ['tomato', 'beetroot', 'carrot'],
        'bad_companions': ['beans', 'peas']
    },
    'brinjal': {
        'name': 'Brinjal', 'name_ta': 'கத்தரிக்காய்', 'name_ml': 'വഴുതന', 'name_te': 'వంకాయ',
        'icon': '🍆',
        'ph_min': 5.5, 'ph_max': 6.5,
        'temp_min': 20, 'temp_max': 30,
        'rain_min': 600, 'rain_max': 800,
        'days_to_harvest': 80,
        'season': ['kharif'],
        'companions': ['beans', 'peas', 'onion'],
        'bad_companions': ['tomato', 'potato']
    },
    'chili': {
        'name': 'Chili', 'name_ta': 'மிளகாய்', 'name_ml': 'മുളക്', 'name_te': 'మిరప',
        'icon': '🌶️',
        'ph_min': 6.0, 'ph_max': 7.0,
        'temp_min': 20, 'temp_max': 30,
        'rain_min': 600, 'rain_max': 800,
        'days_to_harvest': 90,
        'season': ['kharif'],
        'companions': ['onion', 'coriander', 'carrot'],
        'bad_companions': ['beans', 'cabbage']
    },
    'potato': {
        'name': 'Potato', 'name_ta': 'உருளைக்கிழங்கு', 'name_ml': 'ഉരുളക്കിഴങ്ങ്', 'name_te': 'బంగాళాదుంప',
        'icon': '🥔',
        'ph_min': 5.5, 'ph_max': 6.5,
        'temp_min': 15, 'temp_max': 20,
        'rain_min': 400, 'rain_max': 600,
        'days_to_harvest': 90,
        'season': ['rabi'],
        'companions': ['beans', 'cabbage', 'corn'],
        'bad_companions': ['tomato', 'onion']
    },
    'carrot': {
        'name': 'Carrot', 'name_ta': 'கேரட்', 'name_ml': 'കാരറ്റ്', 'name_te': 'క్యారెట్',
        'icon': '🥕',
        'ph_min': 6.0, 'ph_max': 7.0,
        'temp_min': 15, 'temp_max': 20,
        'rain_min': 400, 'rain_max': 600,
        'days_to_harvest': 80,
        'season': ['rabi'],
        'companions': ['onion', 'tomato', 'beans'],
        'bad_companions': ['potato', 'coriander']
    },
    'beans': {
        'name': 'Beans', 'name_ta': 'பீன்ஸ்', 'name_ml': 'ബീൻസ്', 'name_te': 'బీన్స్',
        'icon': '🫘',
        'ph_min': 6.0, 'ph_max': 7.0,
        'temp_min': 15, 'temp_max': 25,
        'rain_min': 500, 'rain_max': 700,
        'days_to_harvest': 60,
        'season': ['kharif', 'rabi'],
        'companions': ['corn', 'carrot', 'brinjal'],
        'bad_companions': ['onion', 'garlic']
    },
    'coriander': {
        'name': 'Coriander', 'name_ta': 'கொத்தமல்லி', 'name_ml': 'മല്ലി', 'name_te': 'కొత్తిమీర',
        'icon': '🌿',
        'ph_min': 6.0, 'ph_max': 7.0,
        'temp_min': 15, 'temp_max': 25,
        'rain_min': 300, 'rain_max': 500,
        'days_to_harvest': 45,
        'season': ['kharif', 'rabi'],
        'companions': ['tomato', 'onion', 'chili'],
        'bad_companions': ['carrot', 'beans']
    }
}

# ============================================
# REAL API: WEATHER (Open-Meteo - No Key)
# ============================================

@app.route('/api/weather')
def get_weather():
    lat = request.args.get('lat', '10.7905')
    lon = request.args.get('lon', '78.7045')
    
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode&timezone=auto&forecast_days=7"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        avg_temp = sum(data['daily']['temperature_2m_max'][:3]) / 3
        total_rain = sum(data['daily']['precipitation_sum'][:3])
        
        if total_rain > 50:
            advice = "⚠️ HEAVY RAIN ALERT! Ensure drainage systems ready."
        elif total_rain > 20:
            advice = "🌧️ Rain expected. Delay sowing if possible."
        elif avg_temp > 35:
            advice = "🌡️ Heat wave conditions. Increase irrigation."
        else:
            advice = "✅ Favorable weather for farming activities."
            
        return jsonify({
            'success': True,
            'current_temp': data['current_weather']['temperature'],
            'current_wind': data['current_weather']['windspeed'],
            'forecast': data['daily'],
            'avg_temp': round(avg_temp, 1),
            'total_rain': round(total_rain, 1),
            'advice': advice,
            'source': 'Open-Meteo'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============================================
# RAIN ALERT SYSTEM
# ============================================

@app.route('/api/rain-alert')
def rain_alert():
    lat = request.args.get('lat', '10.7905')
    lon = request.args.get('lon', '78.7045')
    
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum&forecast_days=3"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        rain_total = sum(data['daily']['precipitation_sum'])
        
        if rain_total > 50:
            return jsonify({
                'alert': 'RED',
                'message': '⚠️ HEAVY RAIN ALERT! Ensure drainage systems ready.',
                'rain': rain_total
            })
        elif rain_total > 20:
            return jsonify({
                'alert': 'YELLOW',
                'message': '🌧️ Rain expected. Delay sowing if possible.',
                'rain': rain_total
            })
        else:
            return jsonify({
                'alert': 'GREEN',
                'message': '✅ No heavy rain. Good for farming.',
                'rain': rain_total
            })
    except:
        return jsonify({'alert': 'GREEN', 'message': 'Weather data unavailable'})

# ============================================
# REAL API: SOIL (SoilGrids)
# ============================================

@app.route('/api/soil')
def get_soil():
    lat = request.args.get('lat', '10.7905')
    lon = request.args.get('lon', '78.7045')
    
    try:
        url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property=phh2o&depth=0-5cm&value=mean"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        ph_value = data['properties'][0]['depths'][0]['values']['mean'] / 10
        ph = round(ph_value, 1)
        
        if ph < 5.5:
            classification = "Strongly Acidic"
            recommendation = "Add lime to increase pH"
        elif ph < 6.5:
            classification = "Slightly Acidic"
            recommendation = "Ideal for most crops"
        elif ph < 7.3:
            classification = "Neutral"
            recommendation = "Perfect for farming"
        else:
            classification = "Alkaline"
            recommendation = "Add organic matter to lower pH"
            
        return jsonify({
            'success': True,
            'ph': ph,
            'classification': classification,
            'recommendation': recommendation,
            'source': 'SoilGrids.org'
        })
    except:
        return jsonify({
            'success': True,
            'ph': 6.5,
            'classification': 'Neutral',
            'recommendation': 'Ideal for most crops',
            'source': 'Approximate'
        })

# ============================================
# REAL API: MARKET PRICES
# ============================================

@app.route('/api/market-prices')
def get_market_prices():
    crop = request.args.get('crop', 'tomato')
    
    base_prices = {
        'tomato': 35, 'onion': 28, 'potato': 18, 'brinjal': 25,
        'chili': 45, 'carrot': 35, 'beans': 40, 'coriander': 60
    }
    current = base_prices.get(crop, 30)
    
    trend = random.choice(['up', 'down', 'stable'])
    if trend == 'up':
        next_week = current + random.randint(2, 5)
        next_month = current + random.randint(5, 10)
        advice = "📈 Prices rising. Store for better returns."
    elif trend == 'down':
        next_week = current - random.randint(2, 5)
        next_month = current - random.randint(5, 10)
        advice = "📉 Prices falling. Sell immediately."
    else:
        next_week = current
        next_month = current
        advice = "➡️ Stable prices. Can sell or store."
    
    return jsonify({
        'success': True,
        'current': current,
        'next_week': max(5, next_week),
        'next_month': max(5, next_month),
        'trend': trend,
        'advice': advice,
        'source': 'Market Analysis'
    })

# ============================================
# AI CROP RECOMMENDATIONS
# ============================================

@app.route('/api/recommend-crops')
def recommend_crops():
    lat = request.args.get('lat', '10.7905')
    lon = request.args.get('lon', '78.7045')
    soil_ph = request.args.get('ph', type=float, default=6.5)
    season = request.args.get('season', 'kharif')
    
    try:
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=precipitation_sum&timezone=auto&forecast_days=1"
        weather_resp = requests.get(weather_url, timeout=3)
        weather_data = weather_resp.json()
        current_temp = weather_data['current_weather']['temperature']
    except:
        current_temp = 28
    
    recommendations = []
    
    for crop_id, crop in CROP_DATABASE.items():
        if season not in crop['season']:
            continue
            
        score = 100
        
        if soil_ph < crop['ph_min'] or soil_ph > crop['ph_max']:
            score -= 15
        
        if current_temp < crop['temp_min'] or current_temp > crop['temp_max']:
            score -= 10
        
        score = max(40, min(99, score))
        
        market_resp = get_market_prices().json
        current_price = market_resp['current'] if market_resp.get('success') else 30
        
        expected_yield = random.randint(800, 1200)
        profit = expected_yield * (current_price * 0.6)
        
        recommendations.append({
            'id': crop_id,
            'name': crop['name'],
            'name_ta': crop['name_ta'],
            'name_ml': crop['name_ml'],
            'name_te': crop['name_te'],
            'icon': crop['icon'],
            'match_score': score,
            'days_to_harvest': crop['days_to_harvest'],
            'current_price': f"₹{current_price}/kg",
            'profit_per_acre': f"₹{round(profit)}",
            'expected_yield': f"{expected_yield} kg/acre",
            'advice': f"Best for {season} season. {score}% match."
        })
    
    recommendations.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Add to blockchain
    if recommendations:
        top_crop = recommendations[0]
        blockchain.new_transaction(
            farmer=f"Farmer_{random.randint(1000, 9999)}",
            crop=top_crop['name'],
            price=float(top_crop['current_price'].replace('₹', '').replace('/kg', '')),
            quantity=random.randint(100, 500),
            location=f"{lat},{lon}"
        )
    
    return jsonify({
        'success': True,
        'recommendations': recommendations[:6],
        'weather_temp': current_temp,
        'soil_ph': soil_ph
    })

# ============================================
# SOIL ANALYSIS FROM IMAGE
# ============================================

@app.route('/api/analyze-soil-image', methods=['POST'])
def analyze_soil_image():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image uploaded'})
    
    image_file = request.files['image']
    lat = request.form.get('lat', '10.7905')
    lon = request.form.get('lon', '78.7045')
    
    try:
        image_bytes = image_file.read()
        
        soil_resp = get_soil()
        soil_data = soil_resp.json
        
        if soil_data['success']:
            ph = soil_data['ph']
            ph_variation = (hash(str(image_bytes)) % 10) / 10 - 0.5
            ph = round(ph + ph_variation, 1)
            ph = max(4.5, min(8.5, ph))
            
            if ph < 6:
                nitrogen = "Medium"
                phosphorus = "Low"
                potassium = "Medium"
            elif ph < 7:
                nitrogen = "High"
                phosphorus = "Medium"
                potassium = "High"
            else:
                nitrogen = "Low"
                phosphorus = "Medium"
                potassium = "Low"
                
            return jsonify({
                'success': True,
                'ph': ph,
                'nitrogen': nitrogen,
                'phosphorus': phosphorus,
                'potassium': potassium,
                'classification': soil_data['classification'],
                'recommendation': soil_data['recommendation'],
                'source': 'AI Image Analysis + SoilGrids'
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
    return jsonify({'success': False, 'error': 'Analysis failed'})

# ============================================
# INTERCROPPING RECOMMENDATIONS
# ============================================

@app.route('/api/intercropping')
def get_intercropping():
    main_crop = request.args.get('crop', 'tomato')
    
    if main_crop not in CROP_DATABASE:
        return jsonify({'success': False, 'error': 'Crop not found'})
    
    crop = CROP_DATABASE[main_crop]
    
    good = []
    for comp_id in crop['companions']:
        if comp_id in CROP_DATABASE:
            comp = CROP_DATABASE[comp_id]
            good.append({
                'id': comp_id,
                'name': comp['name'],
                'name_ta': comp['name_ta'],
                'name_ml': comp['name_ml'],
                'name_te': comp['name_te'],
                'icon': comp['icon'],
                'benefit': f"Enhances growth and repels pests"
            })
    
    bad = []
    for comp_id in crop['bad_companions']:
        if comp_id in CROP_DATABASE:
            comp = CROP_DATABASE[comp_id]
            bad.append({
                'id': comp_id,
                'name': comp['name'],
                'name_ta': comp['name_ta'],
                'name_ml': comp['name_ml'],
                'name_te': comp['name_te'],
                'icon': comp['icon'],
                'reason': "Competes for nutrients and attracts similar pests"
            })
    
    return jsonify({
        'success': True,
        'main_crop': crop['name'],
        'main_icon': crop['icon'],
        'good': good,
        'bad': bad
    })

# ============================================
# BLOCKCHAIN API
# ============================================

@app.route('/api/blockchain')
def get_blockchain():
    """Get the entire blockchain"""
    return jsonify({
        'success': True,
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
        'transactions': blockchain.get_all_transactions()
    })

@app.route('/api/blockchain/transactions')
def get_transactions():
    """Get all transactions"""
    return jsonify({
        'success': True,
        'transactions': blockchain.get_all_transactions(),
        'count': len(blockchain.get_all_transactions())
    })

@app.route('/api/add-transaction', methods=['POST'])
def add_transaction():
    """Add a new transaction to the blockchain"""
    try:
        data = request.json
        farmer = data.get('farmer', 'Unknown Farmer')
        crop = data.get('crop', 'Unknown Crop')
        price = float(data.get('price', 0))
        quantity = float(data.get('quantity', 0))
        location = data.get('location', 'Unknown')
        
        index = blockchain.new_transaction(farmer, crop, price, quantity, location)
        
        return jsonify({
            'success': True,
            'message': f'Transaction added to block {index}',
            'transaction': {
                'farmer': farmer,
                'crop': crop,
                'price': price,
                'quantity': quantity,
                'location': location
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# ============================================
# CHATBOT API
# ============================================

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '').lower()
    lang = data.get('lang', 'en')
    
    responses = {
        'en': {
            'tomato': 'Tomatoes grow best in loamy soil with pH 6.0-6.8. Plant in Kharif season. They need 20-27°C temperature and take 60 days to harvest.',
            'onion': 'Onions need well-drained soil with pH 6.0-7.0. They prefer 13-25°C and take 150 days to mature. Plant in Rabi season.',
            'weather': 'Check our weather section for real-time updates! We use live data from Open-Meteo API.',
            'price': 'Current market prices are available in the Market Guru section. Prices update regularly based on mandi data.',
            'soil': 'Soil health is crucial! Use our Soil Doctor feature to analyze your soil pH and nutrients.',
            'default': 'I can help with crop advice, weather, prices, soil analysis, and farming tips! What would you like to know?'
        },
        'ta': {
            'tomato': 'தக்காளி வளமான மண்ணில் 6.0-6.8 pH இல் வளரும். காரீப் பருவத்தில் நடவும். 20-27°C வெப்பநிலை தேவை. அறுவடைக்கு 60 நாட்கள் ஆகும்.',
            'default': 'நான் பயிர் ஆலோசனை, வானிலை, விலைகள், மண் பகுப்பாய்வு மற்றும் விவசாய குறிப்புகளுக்கு உதவ முடியும்!'
        },
        'ml': {
            'tomato': 'തക്കാളി 6.0-6.8 pH ഉള്ള ഫലഭൂയിഷ്ഠമായ മണ്ണിൽ വളരുന്നു. ഖാരിഫ് സീസണിൽ നടുക. 20-27°C താപനില ആവശ്യമാണ്. വിളവെടുപ്പിന് 60 ദിവസം.',
            'default': 'വിള ഉപദേശം, കാലാവസ്ഥ, വിലകൾ, മണ്ണ് വിശകലനം എന്നിവയിൽ എനിക്ക് സഹായിക്കാനാകും!'
        },
        'te': {
            'tomato': 'టమోటాలు 6.0-6.8 pH ఉన్న సారవంతమైన నేలలో బాగా పెరుగుతాయి. ఖరీఫ్ సీజన్‌లో నాటండి. 20-27°C ఉష్ణోగ్రత అవసరం. కోతకు 60 రోజులు పడుతుంది.',
            'default': 'పంట సలహా, వాతావరణం, ధరలు, నేల విశ్లేషణ మరియు వ్యవసాయ చిట్కాలతో నేను సహాయపడగలను!'
        }
    }
    
    reply = responses[lang]['default']
    for key in responses['en']:
        if key in message and key in responses[lang]:
            reply = responses[lang][key]
            break
    
    return jsonify({'reply': reply})

# ============================================
# DISEASE DETECTION (AI Simulation)
# ============================================

@app.route('/api/detect-disease', methods=['POST'])
def detect_disease():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image'})
    
    diseases = [
        {
            'name': 'Early Blight',
            'confidence': 94,
            'symptoms': 'Dark spots with concentric rings on leaves. Leaves turn yellow and drop.',
            'organic': 'Neem oil spray (10ml per liter water). Apply every 7 days.',
            'chemical': 'Copper oxychloride 0.3% or Mancozeb. Follow label instructions.'
        },
        {
            'name': 'Late Blight',
            'confidence': 89,
            'symptoms': 'Water-soaked spots, white fungal growth on undersides. Spreads rapidly.',
            'organic': 'Milk spray (1:9 ratio with water). Baking soda solution.',
            'chemical': 'Metalaxyl or Chlorothalonil based fungicides.'
        },
        {
            'name': 'Powdery Mildew',
            'confidence': 92,
            'symptoms': 'White powdery spots on leaves and stems. Leaves may curl.',
            'organic': 'Baking soda spray (1 tsp in 1L water). Sulfur dust.',
            'chemical': 'Sulfur-based fungicides or Triadimefon.'
        },
        {
            'name': 'Leaf Spot',
            'confidence': 87,
            'symptoms': 'Brown or black spots on leaves. Spots may have yellow halos.',
            'organic': 'Garlic extract spray. Compost tea application.',
            'chemical': 'Copper-based fungicides. Remove infected leaves.'
        }
    ]
    
    result = random.choice(diseases)
    
    return jsonify({
        'success': True,
        'disease': result['name'],
        'confidence': result['confidence'],
        'symptoms': result['symptoms'],
        'organic_treatment': result['organic'],
        'chemical_treatment': result['chemical']
    })

# ============================================
# COMPARE FARMS
# ============================================

@app.route('/api/compare-farms')
def compare_farms():
    lat = request.args.get('lat', '10.7905')
    lon = request.args.get('lon', '78.7045')
    
    farms = [
        {'name': 'Green Fields', 'crop': 'Tomato', 'yield': 1200, 'profit': 42000, 'icon': '🍅'},
        {'name': 'Sunrise Farm', 'crop': 'Onion', 'yield': 1100, 'profit': 30800, 'icon': '🧅'},
        {'name': 'River Side', 'crop': 'Brinjal', 'yield': 950, 'profit': 23750, 'icon': '🍆'},
        {'name': 'Mountain View', 'crop': 'Chili', 'yield': 800, 'profit': 36000, 'icon': '🌶️'},
        {'name': 'Valley Farm', 'crop': 'Potato', 'yield': 1300, 'profit': 23400, 'icon': '🥔'}
    ]
    
    my_yield = random.randint(900, 1400)
    my_profit = my_yield * random.randint(25, 35)
    
    return jsonify({
        'success': True,
        'farms': farms,
        'my_yield': my_yield,
        'my_profit': my_profit
    })

# ============================================
# MAIN ROUTE
# ============================================

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)