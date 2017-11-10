# Blockchain
Creating a simple blockchain to interact through API endpoints to better understand the topic. API queries are retrieved through cURL / Postman application

# API Endpoints
  - Mine: Calculates the Proof of Work, rewards with the user with a code which is added to a transaction. A new block is forged with this transaction and is added to the chain
  
  - New_Transaction: Verifies data to be sent in the POST request then creates a new transaction to be added to the Block.
  
  - Full Chain: Displays full information from the blockchain 

  - Register_nodes: Lets a node on the network know about neighvour nodes
  
  - Consensus: Uses the consensus algorithm to resolve conflicts to ensure a node has the correct chain (Correct chain =
  longest valid chain available)