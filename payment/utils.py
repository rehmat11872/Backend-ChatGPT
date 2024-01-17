import requests
import base64

def generate_access_token():
    try:
        PAYPAL_CLIENT_ID = "AVGQqqoCWFOUSTTxe_MzwuKokUsIutWzD5qVzIx2azBj6sWPDEdLAoxI9a4fqcIW3P4MeHYPgpB2odkc"
        PAYPAL_CLIENT_SECRET = "EAjQDJJHcoJC5eTnRIVSHvGKg-8HAZpKXLcj8BDijDTG9oi7eGlAi-5ucHYt5Cv6xNbNjl_HWNiFmAk7"

        if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
            raise ValueError("MISSING_API_CREDENTIALS")

        auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {"grant_type": "client_credentials"}

        response = requests.post("https://api-m.sandbox.paypal.com/v1/oauth2/token", headers=headers, data=payload)
        data = response.json()

        return data.get("access_token")

    except Exception as e:
        print(f"Failed to generate Access Token: {e}")
        return None
