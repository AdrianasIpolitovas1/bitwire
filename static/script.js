const connectWalletButton = document.getElementById('connect-wallet');
const sendEthButton = document.getElementById('send-eth');

let userAddress = '';

connectWalletButton.addEventListener('click', async () => {
  if (typeof window.ethereum !== 'undefined') {
    try {
      // Request account access from MetaMask
      const accounts = await ethereum.request({ method: 'eth_requestAccounts' });
      userAddress = accounts[0];
      
      connectWalletButton.innerHTML = `Connected: ${userAddress.slice(0, 6)}...${userAddress.slice(-4)}`;
      connectWalletButton.disabled = true;
      sendEthButton.disabled = false;
    } catch (error) {
      console.error('User rejected the connection request.');
    }
  } else {
    alert('MetaMask is not installed. Please install MetaMask to use this feature.');
  }
});

sendEthButton.addEventListener('click', async () => {
  if (userAddress) {
    try {
      const response = await fetch('/send_eth', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          to_address: userAddress
        })
      });
      
      const result = await response.json();
      if (response.ok) {
        alert(`Transaction Hash: ${result.txn_hash}`);
      } else {
        alert(`Error: ${result.error}`);
      }
    } catch (error) {
      console.error('Transaction failed:', error);
      alert('Transaction failed.');
    }
  }
});
