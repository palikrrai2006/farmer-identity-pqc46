import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from pqc import AESEncryption, KyberKEM, DilithiumSignature
from database.models import db, Farmer
from ipfs.ipfs_client import IPFSClient
from blockchain.contract import FarmerContract

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{BASE_DIR}/farmers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "running", "message": "Farmer Identity PQC API"})


@app.route('/farmer/register', methods=['POST'])
def register_farmer():
    data = request.get_json()

    if not data or 'farmer_id' not in data or 'biometric' not in data:
        return jsonify({"error": "farmer_id and biometric required"}), 400

    farmer_id = data['farmer_id']
    biometric = data['biometric'].encode()

    if Farmer.query.filter_by(farmer_id=farmer_id).first():
        return jsonify({"error": "Farmer already registered"}), 409

    # Step 1: SHA3-256 hash
    bio_hash = AESEncryption.hash_sha3_256(biometric)

    # Step 2: Kyber KEM -> shared secret
    kyber = KyberKEM()
    kyber_keys = kyber.generate_keypair()
    encap = kyber.encapsulate(kyber_keys['public_key'])
    shared_secret = encap['shared_secret']

    # Step 3: AES encrypt using Kyber shared secret as key
    aes = AESEncryption(key=shared_secret[:32])
    encrypted = aes.encrypt(biometric)

    # Step 4: Dilithium sign the record
    dil = DilithiumSignature()
    dil_keys = dil.generate_keypair()
    record_bytes = f"{farmer_id}:{bio_hash}".encode()
    signature = dil.sign(record_bytes, dil_keys['secret_key'])

    # Step 5: Upload encrypted data to IPFS
    ipfs = IPFSClient()
    ipfs_data = {
        "farmer_id": farmer_id,
        "bio_hash": bio_hash,
        "encrypted_bio": encrypted['ciphertext'].hex(),
        "nonce": encrypted['nonce'].hex(),
        "kyber_ciphertext": encap['ciphertext'].hex()
    }
    cid = ipfs.upload(ipfs_data)

    # Step 6: Store CID on blockchain
    bc = FarmerContract()
    tx_hash = bc.register_farmer(farmer_id, bio_hash, cid)

    # Step 7: Save everything to DB
    farmer = Farmer(
        farmer_id=farmer_id,
        bio_hash=bio_hash,
        encrypted_bio=encrypted['ciphertext'].hex(),
        nonce=encrypted['nonce'].hex(),
        aes_key=shared_secret[:32].hex(),
        kyber_public_key=kyber_keys['public_key'].hex(),
        dil_public_key=dil_keys['public_key'].hex(),
        signature=signature.hex(),
        ipfs_cid=cid,
        tx_hash=tx_hash,
        status='enrolled'
    )
    db.session.add(farmer)
    db.session.commit()

    return jsonify({
        "message": "Farmer enrolled successfully",
        "farmer_id": farmer_id,
        "bio_hash": bio_hash,
        "ipfs_cid": cid,
        "tx_hash": tx_hash,
        "status": "enrolled"
    }), 201


@app.route('/farmer/verify', methods=['POST'])
def verify_farmer():
    data = request.get_json()

    if not data or 'farmer_id' not in data or 'biometric' not in data:
        return jsonify({"error": "farmer_id and biometric required"}), 400

    farmer_id = data['farmer_id']
    biometric = data['biometric'].encode()

    farmer = Farmer.query.filter_by(farmer_id=farmer_id).first()
    if not farmer:
        return jsonify({"error": "Farmer not found"}), 404

    incoming_hash = AESEncryption.hash_sha3_256(biometric)

    if incoming_hash == farmer.bio_hash:
        bc = FarmerContract()
        bc_farmer = bc.get_farmer(farmer_id)
        return jsonify({
            "message": "Farmer verified successfully",
            "farmer_id": farmer_id,
            "ipfs_cid": farmer.ipfs_cid,
            "tx_hash": farmer.tx_hash,
            "blockchain_cid": bc_farmer['ipfs_cid'],
            "status": "verified"
        }), 200
    else:
        return jsonify({
            "message": "Verification failed - biometric mismatch",
            "farmer_id": farmer_id,
            "status": "rejected"
        }), 401


@app.route('/farmer/<farmer_id>', methods=['GET'])
def get_farmer(farmer_id):
    farmer = Farmer.query.filter_by(farmer_id=farmer_id).first()
    if not farmer:
        return jsonify({"error": "Farmer not found"}), 404
    return jsonify(farmer.to_dict()), 200


@app.route('/farmers', methods=['GET'])
def list_farmers():
    farmers = Farmer.query.all()
    return jsonify({
        "total": len(farmers),
        "farmers": [f.to_dict() for f in farmers]
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
