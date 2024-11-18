Implementation of Smart Contract in P2P Energy Trading

The file "p2p_trades_final_dict_BT.pkl" is the result of possible trades between participants in a theoretical Energy Community. 
The main information of the trades are: 
  1) Buyer name (string);
  2) Seller name (string);
  3) Quantity in kWh (float);
  4) Price in EUR (float);
  5) DeliveryTime (timestamp 'YYYY-MM-DD HH:MM:SS')

The Smart Contract is develop in Solidity and then applyed through Python file using Web3.py library to connect to Blockchain environment. 

This Smart Contract guarantee: 
  1) Registration of a contract with identification of buyer, seller, quantity, price, delivery time (using the conversions needed to work in Solidity, e.g. convert floats to ints)
  2) Transference of (quantity * price) from buyer to seller
  3) Events to store and easy visualization of Registrations and Transferences
  4) Low gas costs, using "Proof-of-Authority" as consensus mechanism - all participants in the Community are authorized to validate transactions and add new blocks)
  5) Integration with Python and Ganache test environment

Through a test environment, such as Ganache, should be proof that the trades initially sotared in a Python Dictionary now are registered in a Blockchain (with Events to track trades,
such as name of buyer and seller, quantity in kWh, price in EUR, value transfered in EUR, deliverytime.
