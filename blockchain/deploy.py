import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web3 import Web3
from solcx import compile_source, install_solc
from dotenv import load_dotenv

load_dotenv()

GANACHE_URL       = os.getenv("GANACHE_URL", "HTTP://127.0.0.1:7545")
DEPLOYER_ADDRESS  = os.getenv("DEPLOYER_ADDRESS")
DEPLOYER_PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY")

def deploy_contract():
    # Connect to Ganache
    w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    assert w3.is_connected(), "Cannot connect to Ganache!"
    print(f"Connected to Ganache: {GANACHE_URL}")

    # Install solc compiler
    install_solc("0.8.0")

    # Read contract source
    contract_path = os.path.join(os.path.dirname(__file__), "FarmerRegistry.sol")
    with open(contract_path, "r") as f:
        source = f.read()

    # Compile
    compiled = compile_source(source, output_values=["abi", "bin"], solc_version="0.8.0")
    contract_interface = compiled["<stdin>:FarmerRegistry"]
    abi = contract_interface["abi"]
    bytecode = contract_interface["bin"]

    # Deploy
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    nonce = w3.eth.get_transaction_count(DEPLOYER_ADDRESS)

    tx = contract.constructor().build_transaction({
        "from":     DEPLOYER_ADDRESS,
        "nonce":    nonce,
        "gas":      3000000,
        "gasPrice": w3.to_wei("20", "gwei")
    })

    signed_tx = w3.eth.account.sign_transaction(tx, DEPLOYER_PRIVATE_KEY)
    tx_hash   = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt   = w3.eth.wait_for_transaction_receipt(tx_hash)

    contract_address = receipt.contractAddress
    print(f"Contract deployed at: {contract_address}")

    # Save ABI and address to .env
    import json
    abi_path = os.path.join(os.path.dirname(__file__), "contract_abi.json")
    with open(abi_path, "w") as f:
        json.dump(abi, f)

    print(f"ABI saved to blockchain/contract_abi.json")
    print(f"Add this to .env:")
    print(f"CONTRACT_ADDRESS={contract_address}")

    return contract_address

if __name__ == "__main__":
    deploy_contract()