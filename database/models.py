from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Farmer(db.Model):
    __tablename__ = 'farmers'

    id               = db.Column(db.Integer, primary_key=True)
    farmer_id        = db.Column(db.String(50), unique=True, nullable=False)
    bio_hash         = db.Column(db.String(64), nullable=False)
    encrypted_bio    = db.Column(db.Text, nullable=False)
    nonce            = db.Column(db.String(64), nullable=False)
    aes_key          = db.Column(db.String(64), nullable=False)
    kyber_public_key = db.Column(db.Text, nullable=False)
    dil_public_key   = db.Column(db.Text, nullable=False)
    signature        = db.Column(db.Text, nullable=False)
    ipfs_cid         = db.Column(db.String(100), nullable=True)   # ← NEW
    status           = db.Column(db.String(20), default='enrolled')

    def to_dict(self):
        return {
            "farmer_id": self.farmer_id,
            "bio_hash":  self.bio_hash,
            "ipfs_cid":  self.ipfs_cid,
            "status":    self.status
        }