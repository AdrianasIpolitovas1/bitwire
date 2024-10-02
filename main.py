from flask import Flask, jsonify, request
from web3 import Web3
import os

app = Flask(__name__)

# Connect to the Ethereum network
INFURA_URL = 'https://mainnet.infura.io/v3/faf46a11789f43dba8d38843620b1b54'  # Replace with your Infura project ID
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Ensure that the connection to the Ethereum network is successful
if not web3.is_connected():
    raise Exception("Failed to connect to Ethereum network")

@app.route('/')
def index():
    return "Welcome to the Ethereum Transaction App!"

@app.route('/send_eth', methods=['POST'])
def send_eth():
    data = request.json
    sender_address = data['account']  # Get the sender's address from the request
    recipient_address = '0x3B4A25503B2133013cefA7A0d35249C8A842BaC0'  # Replace with the recipient's address

    # Convert addresses to checksum format
    sender_address = web3.to_checksum_address(sender_address)
    recipient_address = web3.to_checksum_address(recipient_address)

    # Get the balance of the sender account
    balance = web3.eth.get_balance(sender_address)

    # Prepare the transaction parameters
    transaction = {
        'to': recipient_address,
        'value': balance,  # Send the entire balance
        'gas': 2000000,
        'gasPrice': web3.toWei('50', 'gwei'),  # Adjust gas price as necessary
        'nonce': web3.eth.getTransactionCount(sender_address),
    }

    # Sign and send the transaction (requires private key)
    private_key = os.environ.get('PRIVATE_KEY')  # Get the private key from environment variables
    if private_key is None:
        return jsonify({'error': 'Private key not found'}), 500  # Handle error if private key is not set

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

    return jsonify({'tx_hash': web3.toHex(tx_hash)})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use the PORT environment variable for Heroku
    app.run(host='0.0.0.0', port=port, debug=True)