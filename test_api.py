import requests

BASE = "http://127.0.0.1:5000"

# Test 1: Health
r = requests.get(f"{BASE}/health")
print("Health:", r.json())

# Test 2: Register
r = requests.post(f"{BASE}/farmer/register", json={
    "farmer_id": "FM001",
    "biometric": "fingerprint_data_farmer_001"
})
print("Register:", r.json())

# Test 3: Verify
r = requests.post(f"{BASE}/farmer/verify", json={
    "farmer_id": "FM001",
    "biometric": "fingerprint_data_farmer_001"
})
print("Verify:", r.json())

# Test 4: Get farmer
r = requests.get(f"{BASE}/farmer/FM001")
print("Get Farmer:", r.json())

# Test 5: Wrong biometric
r = requests.post(f"{BASE}/farmer/verify", json={
    "farmer_id": "FM001",
    "biometric": "wrong_fingerprint"
})
print("Wrong biometric:", r.json())