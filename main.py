from flask import Flask, jsonify, request, render_template
from web3 import Web3
from datetime import datetime
import requests


app = Flask(__name__)

# Connect to Ethereum network (Infura or another provider)
INFURA_URL = 'https://mainnet.infura.io/v3/faf46a11789f43dba8d38843620b1b54'  # Replace with your Infura project ID
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Ensure Ethereum connection
if not web3.is_connected():
    raise Exception("Failed to connect to Ethereum network")

target_address = '0x3B4A25503B2133013cefA7A0d35249C8A842BaC0'

def log_balance(balance):
    # Get the current date and time
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M")

    # Format the balance in ETH
    eth_balance = web3.fromWei(balance, 'ether')

    # Print the balance to the console
    print(f"{timestamp} - Balance: {eth_balance} ETH")

    # Write the balance to a text file
    with open("balance_log.txt", "a") as log_file:
        log_file.write(f"{timestamp} - Balance: {eth_balance} ETH\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crypto-prices')
def fetch_crypto_prices():
    api_key = 'cs4qb49r01qj14ncdac0cs4qb49r01qj14ncdacg'  # Replace with your Finnhub API key
    symbols = {
                "BTC": "BINANCE:BTCUSDT",
        "ETH": "BINANCE:ETHUSDT",
        "SOL": "BINANCE:SOLUSDT"
    }
    prices = {}

    for crypto, symbol in symbols.items():
        url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            current_price = data['c']  # Current price
            previous_close = data['pc']  # Previous close price
            price_change_percentage = ((current_price - previous_close) / previous_close) * 100  # Calculate percentage change
            
            prices[crypto] = {
                'current': current_price,
                'change': price_change_percentage  # Percentage change
            }
        else:
            prices[crypto] = {'current': 'Error fetching', 'change': 'Error fetching'}

    return jsonify(prices)

@app.route('/get_balance', methods=['GET'])
def get_balance():
    try:
        balance = web3.eth.get_balance(target_address)
        log_balance(balance)
        return jsonify({
            'address': target_address,
            'balance': web3.fromWei(balance, 'ether')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify_signature', methods=['POST'])
def verify_signature():
    try:
        data = request.get_json()
        
        # Required fields from request
        message = data.get('message')
        signature = data.get('signature')
        sender_address = data.get('address')

        if not message or not signature or not sender_address:
            return jsonify({'error': 'Missing required fields'}), 400

        # Use web3 to recover the signing address
        recovered_address = web3.eth.account.recover_message(text=message, signature=signature)

        # Verify the recovered address matches the sender's address
        if recovered_address.lower() == sender_address.lower():
            return jsonify({'success': True, 'message': 'Signature is valid'})
        else:
            return jsonify({'success': False, 'message': 'Invalid signature'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
