import hashlib
import json

from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

class Blockchain(object):
    '''
    Responsible for managing the Chain
        - Stores transactions
        - Helper methods for adding new blocks
    '''
    def __init__(self):
        self.chain = []  # Stores blockchain
        self.current_transactions = []  # Stores current transactions

        # Create new genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        '''

        Creates a new block in the Blockchain

        :param proof: Proof given by the 'Proof of Work' algo
        :param previous_hash: Hash of previous Block
        :return: dict New block
        '''

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        # Reset current list of transactions
        self.current_transactions = []
        self.chain.append(block)
        return block


    def new_transaction(self, sender, recipient, amount):
        '''

        Creates new transaction to go into next mined block

        :param sender: Address of sender
        :param recipient: Address of receiver
        :param amount: Amount sent / received
        :return: Index of block that will hold this transaction
        '''

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })  # Adds new transaction to list

        # Returns index of block which trans will be added to, the next one to be mined
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        '''

        Create a SHA-256 Hash of block

        :param block: dict block
        :return: Hash str
        '''
        # Make an ordered Dict for consistent hashes -> keeps immutability (?)
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        '''

        Simple PoW
            - Find a number 'p' -> hash(pp') contains leading 4 0s, where p is the previous p'
            - p is the previous proof, and p' is the new proof

        :param last_proof:
        :return:
        '''

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates proof -> Does hash(last_proofm proof) contain 4 leading 0s?

        :param last_proof: Previous Proof
        :param proof:  Current proof
        :return: bool True if correct, false if not
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

# Make Node
app = Flask(__name__)

# Gen globally unqiue addres for node
# Random name for node
node_id = str(uuid4()).replace('-', '')

# Instantiate blockchain
blockchain = Blockchain()


# API Routes / Endpoints

# Mining Endpoint
@app.route('/mine', methods=['GET'])
def mine():
    '''
        - Calculate PoW
        - Reward miner by adding a Transaction giving user 1 Coin
        - Forge new Block by adding it to Chain
    :return:
    '''
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Get coin for finding proof
    # Sender = 0, that node ahs mined coin
    blockchain.new_transaction(
        sender=0,
        recipient=node_id,
        amount=1
    )

    # Forge block, add to chain
    block = blockchain.new_block(proof)

    resp = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(resp), 200

# Transaction Endpoint
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check for required fields of POST data
    req = ['sender', 'recipient', 'amount']
    if not all(val in values for val in req):
        return 'Missing values', 400

    # Create new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    resp = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(resp), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    resp = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(resp), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)