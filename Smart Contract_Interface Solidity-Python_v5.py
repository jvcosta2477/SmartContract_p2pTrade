### Python interaction is necessary the installations

from web3 import Web3 # blockchain interaction 
from solcx import compile_source # compiling Solidity code
import solcx 

# Install and set Solidity compiler version
solcx.install_solc('0.8.18')
solcx.set_solc_version('0.8.18')

# Connect to Ethereum node (local Ganache)
w3 = Web3(Web3.HTTPProvider('HTTP://127.0.0.1:7545'))  # ganache_url
network_id = 5777 
port = 7545

# Check if connected
if w3.is_connected():
    print("Successfully connected to Ganache!")
else:
    print("Connection failed. Please check if Ganache is running and the URL is correct.")

w3.eth.default_account = w3.eth.accounts[0]

# Solidity source code for the contract
solidity_code = '''
// SPDX-License-Identifier: MIT
pragma solidity 0.8.18;

contract p2pTrade {
    struct Trade {
        address payable buyerAddress; // Account of the buyer
        address payable sellerAddress; // Account of the seller
        uint256 quantity; // Energy trade in watt-hours (Wh)
        uint256 priceInWei; // Price per unit of energy, in Wei (smallest unit of Ether)
        uint256 delivery; // Unix timestamp for when the delivery will occur
        bool isFinalized; // Flag indicating whether the trade has been finalized
    }

    // Mapping to store trades
    mapping(uint256 => Trade) private trades;
    uint256 private tradeCounter; // Counter to track trade IDs

    // Events to notify when trades are registered or finalized
    event TradeRegistered(
        uint256 indexed tradeId,
        address indexed buyerAddress,
        address indexed sellerAddress,
        uint256 quantity,
        uint256 priceInWei,
        uint256 delivery
    );

    event TradeFinalized(
        uint256 indexed tradeId,
        uint256 totalPriceInWei
    );

    // Modifier to check if msg.sender is the buyer
    modifier onlyBuyer(uint256 tradeId) {
        require(msg.sender == trades[tradeId].buyerAddress, "Only the buyer can perform this action.");
        _;
    }

    // Modifier to check if msg.sender is the seller
    modifier onlySeller(uint256 tradeId) {
        require(msg.sender == trades[tradeId].sellerAddress, "Only the seller can perform this action.");
        _;
    }

    // Register a new trade (only callable by the buyer or seller)
    function registerTrade(
        address payable _buyerAddress,
        address payable _sellerAddress,
        uint256 _quantity,
        uint256 _priceInWei,
        uint256 _delivery
    ) public {
        // Increment the counter to create a unique trade ID
        tradeCounter++;

        // Store the new trade in the mapping
        trades[tradeCounter] = Trade({
            buyerAddress: _buyerAddress,
            sellerAddress: _sellerAddress,
            quantity: _quantity,
            priceInWei: _priceInWei,
            delivery: _delivery,
            isFinalized: false
        });

        // Emit event to notify that a new trade has been registered
        emit TradeRegistered(
            tradeCounter,
            _buyerAddress,
            _sellerAddress,
            _quantity,
            _priceInWei,
            _delivery
        );
    }
    
    // Finalize the trade and transfer Ether (only callable by the buyer)
    function finalizeTrade(uint256 tradeId) public payable onlyBuyer(tradeId) {
        Trade storage trade = trades[tradeId];
        require(!trade.isFinalized, "Trade has already been finalized.");
        
        uint256 totalPrice = trade.quantity * trade.priceInWei;
        require(msg.value >= totalPrice, "Insufficient Ether sent for the trade.");

        // Transfer Ether to the seller
        trade.sellerAddress.transfer(totalPrice);
        trade.isFinalized = true;

        // Emit event to notify that the trade has been finalized
        emit TradeFinalized(tradeId, totalPrice);

        // Refund any excess Ether sent
        if (msg.value > totalPrice) {
            payable(msg.sender).transfer(msg.value - totalPrice);
        }
    }

    // Retrieve details of a specific trade
    function getTrade(uint256 tradeId) public view returns (
        uint256 delivery,
        address buyer,
        address seller,
        uint256 quantity,
        uint256 priceInWei,
        bool isFinalized
    ) {
        Trade storage trade = trades[tradeId];
        return (
            trade.delivery,
            trade.buyerAddress,
            trade.sellerAddress,
            trade.quantity,
            trade.priceInWei,
            trade.isFinalized
        );
    }
}
'''

# Compile contract
compiled_sol = compile_source(solidity_code)
contract_interface = compiled_sol['<stdin>:p2pTrade']

# Function to deploy contract
def deploy_contract():
    p2pTrade = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
    
    # Deploy the contract with specified 'from' address
    tx_hash = p2pTrade.constructor().transact({'from': w3.eth.accounts[0]})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    # Create contract instance with new address
    contract_instance = w3.eth.contract(address=tx_receipt.contractAddress, abi=contract_interface['abi'])
    print(f"Contract deployed at {tx_receipt.contractAddress}")
    return contract_instance

# Function to register a trade
def register_trade(contract_instance, buyer, seller, quantity, price, delivery):
    tx_hash = contract_instance.functions.registerTrade(
        buyer, seller, quantity, price, delivery
    ).transact({'from': buyer, 'gas': 300000})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Trade registered successfully.")

# Function to finalize a trade
def finalize_trade(contract_instance, trade_id, buyer, quantity, price):
    total_price = quantity * price
    tx_hash = contract_instance.functions.finalizeTrade(trade_id).transact({
        'from': buyer, 
        'value': total_price,
        'gas': 300000
    })
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Trade finalized successfully.")

# Deploy the contract
contract_instance = deploy_contract()


## Import P2P Trades Dictionary
import pickle

# Load the pickled dictionary from the file
with open('p2p_trades_final_dict_BT.pkl', 'rb') as file:
    p2p_trades_final_dict_BT = pickle.load(file)

# Ganache 29x free Ether accounts
address_accounts = [
    '0xcE81C550f6945Ef9a8ED19F4359055de5332Ed3C',
    '0x5504D1410dB562105F1D48c3999E4E0B1c3C176D',
    '0x69267C0a8BE0394c82f77C15dd1182B298aAAe92',
    '0xC7F86685f7e4a573344188C514836477e3c3DC4E',
    '0x4F00Cbd00504fbeF5E046730e1A2ab9616b9C03E',
    '0xc5415f483b39AA095c54896150752675Af9dCF26',
    '0x24E85a49C0663af5eD948Ed7d2DBFEEb14e0B55c',
    '0xF3a9279D8A3E5Ad3F1959DDf5c6FBC2ebe89B378',
    '0x51cBD73A9bCCbcA098Fa9332BB7F519009c4Cc3B',
    '0x7338e53c9187ccE2A20ECD9e0C80e67B41D30329',
    '0x7b6F5d470D70E9613B70aEb3A92eAA763BeeAc64',
    '0xfa7Ff67fa5E9B835266Be64BE0105B1572eE798B',
    '0x25C6dBb6af6416eCec6dFFc4DDa4e263E3C6D84a',
    '0x3b111934Ce9CDa13b2cB37c1dc8C6AD5EE65CF9c',
    '0x6E36634789f7793D9dBA37C8d9337c7C2c092463',
    '0xab7a79DE81a29e46D6298c1a4F5AD2C1e5649144',
    '0x2284c9948a30A76b163bfd45B5A8649E5d1876e4',
    '0xA556f12046E771399DF9ee36f8e398eb44A88a26',
    '0xb761cE5Fcc1869602cAaD886b55c815FB909874e',
    '0x34F853dC8fcF93bB02ba007956Be54Fb17e4Adf0',
    '0xC4373d95F80ABCC1016bFD38341CEe5EE75506D1',
    '0xd2C67040f83a09c117FEc3b9Ba7bFB2d3069D95a',
    '0xB8F7C9e9678a9eF01ad7bFf7d15fC81b620E05f1',
    '0x0Dc5Ad85Cbbe0bA03d244C4c073397C9d553a959',
    '0xfF82986864d97650A50BD5F06491126041e218a3',
    '0xd995814a66A045c171887e970aE631c0ae2F9a78',
    '0xCf5f2544f6B3C57bb9bc6A7Cc56ddA4247Eb96Ab',
    '0x219b3fef7f81d2d39D8B7d3881B2b93b5B7BfF96',
    '0x50261bd0ad7997E1b812e56263144a256676C769'
    ]    

# Wallet account (simulation only)
participants = ['P1'] + [f'C{i}' for i in range(1,29)]
address_dict = {f'{participants[i]}': address_accounts[i] for i in range(0,29)}
   
# Set Smart Contract for each transaction in P2P Market
eth_to_eur = 2300 # exchange rate 1 Ether = 2300 Euros
for key, trades in p2p_trades_final_dict_BT.items(): 
    # 'key' is the Datetime of the trade
    # 'trades' is DataFrame with trade information (buyer, seller, quantity, prices)
    if trades.shape[0] == 0:
        continue # Case there is no trade in this hour 
    else: 
        trade_id = 0
        counter = 0
        for trade in trades.itertuples():
            delivery = key # Datetime
            delivery_unix = int(delivery.timestamp())
            buyer = trade.buyer
            buyer_address = address_dict[buyer]
            seller = trade.seller
            seller_address = address_dict[seller]
            quantity_Wh = int(round(trade.quantity, 3) *1000) # kWh = 10^3 Wh
            price_EUR = round(trade.price, 4) # EUR/kWh
            price_Wei = round((price_EUR / (eth_to_eur * 1000)) * 10**18) # Wei/Wh; 1 Ether = 10^18 Wei
            transfer_EUR = round(quantity_Wh * price_EUR / 1000, 4) # Wh * EUR/kWh * 1[kWh]/1000 [Wh] 
            transfer_Wei =  round(quantity_Wh * price_Wei)
            print(f'Delivery time: {delivery}')
            print(f'Buyer: {buyer}')
            print(f'Seller: {seller}')
            print(f'Quantity [kWh]: {quantity_Wh / 1000}')
            print(f'Price [EUR/kWh]: {price_EUR}')
            print(f'Transfer [EUR]: {transfer_EUR}')
            print(' ')
            print(f'Delivery Unix Timestamp: {delivery_unix}')
            print(f'Buyer Address: {buyer_address}')
            print(f'Seller Address: {seller_address}')
            print(f'Quantity [Wh]: {quantity_Wh}')
            print(f'Price [Wei/Wh]: {price_Wei}')
            print(f'Transfer [Wei]: {transfer_Wei}')
            print(' ')
            print(' ')
            counter += 1
            trade_id += 1
            # Add here the Smart Contract
            register_trade(contract_instance=contract_instance, buyer=buyer_address, seller=seller_address, quantity=quantity_Wh, price=price_Wei, delivery=delivery_unix)
            finalize_trade(contract_instance=contract_instance, trade_id=trade_id, buyer=buyer_address, quantity=quantity_Wh, price=price_Wei)
        if counter >= 4:
            break
