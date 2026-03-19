import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web3 import Web3
from dotenv import load_dotenv
import json

load_dotenv()

GANACHE_URL          = os.getenv("GANACHE_URL", "HTTP://127.0.0.1:7545")
DEPLOYER_ADDRESS     = os.getenv("DEPLOYER_ADDRESS")
DEPLOYER_PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")
CONTRACT_ADDRESS     = os.getenv("CONTRACT_ADDRESS")


class FarmerContract:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
        assert self.w3.is_connected(), "Cannot connect to Ganache!"

        abi_path = os.path.join(os.path.dirname(__file__), "contract_abi.json")
        with open(abi_path, "r") as f:
            abi = json.load(f)

        self.contract = self.w3.eth.contract(
            address=self.w3.to_checksum_address(CONTRACT_ADDRESS),
            abi=abi
        )

    def register_farmer(self, farmer_id: str, bio_hash: str, ipfs_cid: str) -> str:
        """Store farmer record on blockchain. Returns transaction hash."""
        nonce = self.w3.eth.get_transaction_count(DEPLOYER_ADDRESS)
        tx = self.contract.functions.registerFarmer(
            farmer_id, bio_hash, ipfs_cid
        ).build_transaction({
            "from":     DEPLOYER_ADDRESS,
            "nonce":    nonce,
            "gas":      300000,
            "gasPrice": self.w3.to_wei("20", "gwei")
        })
        signed_tx = self.w3.eth.account.sign_transaction(tx, DEPLOYER_PRIVATE_KEY)
        tx_hash   = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt   = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return receipt.transactionHash.hex()

    def get_farmer(self, farmer_id: str) -> dict:
        """Retrieve farmer record from blockchain."""
        farmer_id_str, bio_hash, ipfs_cid, timestamp = \
            self.contract.functions.getFarmer(farmer_id).call()
        return {
            "farmer_id": farmer_id_str,
            "bio_hash":  bio_hash,
            "ipfs_cid":  ipfs_cid,
            "timestamp": timestamp
        }

    def farmer_exists(self, farmer_id: str) -> bool:
        """Check if farmer is registered on blockchain."""
        return self.contract.functions.farmerExists(farmer_id).call()
