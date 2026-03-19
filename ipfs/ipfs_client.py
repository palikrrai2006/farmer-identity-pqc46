import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

PINATA_JWT = os.getenv("PINATA_JWT")

class IPFSClient:
    def __init__(self):
        self.jwt = PINATA_JWT
        self.headers = {
            "Authorization": f"Bearer {self.jwt}"
        }
        self.pin_url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"

    def upload(self, data: dict) -> str:
        """Upload encrypted farmer data to IPFS. Returns CID."""
        payload = {
            "pinataContent": data,
            "pinataMetadata": {
                "name": f"farmer_{data.get('farmer_id', 'unknown')}"
            }
        }
        response = requests.post(
            self.pin_url,
            json=payload,
            headers=self.headers
        )
        if response.status_code == 200:
            cid = response.json()['IpfsHash']
            return cid
        else:
            raise Exception(f"IPFS upload failed: {response.text}")

    def retrieve(self, cid: str) -> dict:
        """Retrieve data from IPFS using CID."""
        url = f"https://gateway.pinata.cloud/ipfs/{cid}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"IPFS retrieve failed: {response.text}")