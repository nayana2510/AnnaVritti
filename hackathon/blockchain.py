# blockchain.py - Blockchain for transparent farming transactions

import hashlib
import json
from time import time

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
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block
    
    def new_transaction(self, farmer, crop, price, quantity, location):
        """Add a new transaction to the current block"""
        self.current_transactions.append({
            'farmer': farmer,
            'crop': crop,
            'price': price,
            'quantity': quantity,
            'location': location,
            'timestamp': time()
        })
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
    
    def proof_of_work(self, last_proof):
        """Simple Proof of Work algorithm"""
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof
    
    @staticmethod
    def valid_proof(last_proof, proof):
        """Validate the proof"""
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"