# generate_client_secret.py
import jwt
from datetime import datetime, timedelta

# Your credentials obtained from Apple
team_id = 'U86KGR5XFU'
client_id = 'com.lawtabby.pdf.sid'
key_id = 'W63JQDWXV8'

private_key_path = 'AuthKey_W63JQDWXV8.p8'

# Load your private key
with open(private_key_path, 'r') as key_file:
    private_key = key_file.read()

# Prepare payload
time_now = datetime.now()
exp_time = time_now + timedelta(days=180)  # Token expires in 180 days
payload = {
    'iss': team_id,
    'iat': int(time_now.timestamp()),
    'exp': int(exp_time.timestamp()),
    'aud': 'https://appleid.apple.com',
    'sub': client_id,
}

# Generate the client secret
client_secret = jwt.encode(payload, private_key, algorithm='ES256', headers={'kid': key_id})
print(client_secret, 'client_secret')
