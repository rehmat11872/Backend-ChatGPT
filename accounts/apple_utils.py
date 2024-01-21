import requests
from datetime import datetime, timedelta
from urllib.parse import parse_qsl, quote, urlencode

from django.core.exceptions import ImproperlyConfigured

import jwt

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.oauth2.client import (
    OAuth2Client,
    OAuth2Error,
)
from project.settings import   APPlE_REDIRECT_URL
from decouple import config

def jwt_encode(*args, **kwargs):
    resp = jwt.encode(*args, **kwargs)
    if isinstance(resp, bytes):
        # For PyJWT <2
        resp = resp.decode("utf-8")
    return resp


class Scope(object):
    EMAIL = "email"
    NAME = "name"


class AppleOAuth2Client(OAuth2Client):
    """
    Custom client because `Sign In With Apple`:
        * requires `response_mode` field in redirect_url
        * requires special `client_secret` as JWT
    """

    def generate_client_secret(self):
        """Create a JWT signed with an apple provided private key"""
        now = datetime.utcnow()
        app = get_adapter(self.request).get_app(self.request, "apple")
        if not app.key:
            raise ImproperlyConfigured("Apple 'key' missing")
        certificate_key = app.settings.get("certificate_key")
        print(certificate_key, 'paras here')
        if not certificate_key:
            raise ImproperlyConfigured("Apple 'certificate_key' missing")
        claims = {
            "iss": app.key,
            "aud": "https://appleid.apple.com",
            "sub": self.get_client_id(),
            "iat": now,
            "exp": now + timedelta(hours=1),
        }
        headers = {"kid": self.consumer_secret, "alg": "ES256"}
        client_secret = jwt_encode(
            payload=claims, key=certificate_key, algorithm="ES256", headers=headers
        )
        return client_secret

    def get_client_id(self):
        """We support multiple client_ids, but use the first one for api calls"""
        return self.consumer_key.split(",")[0]
    

    def get_access_token(self, code, pkce_code_verifier=None):
        token_endpoint = 'https://appleid.apple.com/auth/token'
        # your_client_secret = 'eyJhbGciOiJFUzI1NiIsImtpZCI6Ilc2M0pRRFdYVjgiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJVODZLR1I1WEZVIiwiaWF0IjoxNzA0NDM3MTQyLCJleHAiOjE3MTk5ODkxNDIsImF1ZCI6Imh0dHBzOi8vYXBwbGVpZC5hcHBsZS5jb20iLCJzdWIiOiJjb20ubGF3dGFiYnkucGRmLnNpZCJ9.Kxla2m7FQ5THJaZiOxsP58eiwk4Gn8asJkWB_IyYUUquxEDQ9rTru6saCS3btBWpu35XKXXrmfNfTCtuoLbbXg'
        # your_client_id = 'com.lawtabby.pdf.sid'
        your_client_id = config('SOCIAL_APPLE_CLIENT_ID', default='')
        client_secret = self.generate_client_secret()
        print(client_secret, 'client_sec_____')

        token_params = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': APPlE_REDIRECT_URL,
            # 'redirect_uri': 'https://377a-119-63-138-173.ngrok-free.app',
            'client_id': your_client_id,
            'client_secret': client_secret,
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Your User Agent',
        }

        response = requests.post(token_endpoint, data=token_params, headers=headers)
        print(response.text, 'response')

        if response.status_code != 200 or 'access_token' not in response.json():
            raise OAuth2Error("Error retrieving access token: %s" % response.content)


        access_token = response.json()

        return access_token


    def get_redirect_url(self, authorization_url, extra_params):
        params = {
            "client_id": self.get_client_id(),
            "redirect_uri": self.callback_url,
            "response_mode": "form_post",
            "scope": self.scope,
            "response_type": "code id_token",
        }
        if self.state:
            params["state"] = self.state
        params.update(extra_params)
        return "%s?%s" % (authorization_url, urlencode(params, quote_via=quote))

# import requests
# from datetime import datetime, timedelta
# from urllib.parse import parse_qsl, quote, urlencode

# from django.core.exceptions import ImproperlyConfigured
# import jwt

# from allauth.socialaccount.adapter import get_adapter
# from allauth.socialaccount.providers.oauth2.client import OAuth2Client, OAuth2Error


# from django.conf import settings
# from django.utils import timezone
# import json

# class Scope(object):
#     EMAIL = "email"
#     NAME = "name"

# class AppleOAuth2Client(OAuth2Client):
#     """
#     Custom client for `Sign In With Apple`:
#         * requires `response_mode` field in redirect_url
#         * requires special `client_secret` as JWT
#     """

#     def generate_client_secret(self):
#         team_id = 'U86KGR5XFU'
#         client_id = 'com.lawtabby.pdf.sid'
#         key_id = 'W63JQDWXV8'

#         private_key_path = 'AuthKey_W63JQDWXV8.p8'

#         # Load your private key
#         with open(private_key_path, 'r') as key_file:
#             private_key = key_file.read()

#         # Prepare payload
#         time_now = datetime.now()
#         exp_time = time_now + timedelta(days=180)  # Token expires in 180 days
#         payload = {
#             'iss': team_id,
#             'iat': int(time_now.timestamp()),
#             'exp': int(exp_time.timestamp()),
#             'aud': 'https://appleid.apple.com',
#             'sub': client_id,
#         }

#         # Generate the client secret
#         client_secret = jwt.encode(payload, private_key, algorithm='ES256', headers={'kid': key_id})
#         return client_secret
#     # def generate_client_secret(self):
#     #     """Create a JWT signed with an apple provided private key"""
#     #     now = datetime.utcnow()
#     #     app = get_adapter(self.request).get_app(self.request, "apple")
#     #     if not app.key:
#     #         raise ImproperlyConfigured("Apple 'key' missing")
#     #     certificate_key = app.settings.get("certificate_key")
#     #     print(certificate_key, 'certificate_key')
#     #     if not certificate_key:
#     #         raise ImproperlyConfigured("Apple 'certificate_key' missing")

#     #     # headers = {
#     #     #     "kid": self.consumer_secret,
#     #     #     "alg": "ES256"
#     #     # }

#     #     # payload = {
#     #     #     "iss": app.key,
#     #     #     "aud": "https://appleid.apple.com",
#     #     #     "sub": self.get_client_id(),
#     #     #     "iat": now,
#     #     #     "exp": now + timedelta(hours=1),
#     #     # }
#     #     test = settings.SOCIAL_AUTH_APPLE_PRIVATE_KEY
#     #     print(test, 'paras')

#     #     headers = {
#     #         'kid': settings.SOCIAL_AUTH_APPLE_KEY_ID
#     #         }

#     #     payload = {
#     #         'iss': settings.SOCIAL_AUTH_APPLE_TEAM_ID,
#     #         'iat': timezone.now(),
#     #         'exp': timezone.now() + timedelta(days=180),
#     #         'aud': 'https://appleid.apple.com',
#     #         'sub': settings.CLIENT_ID,
#     #         }
        
#     #     private_key_path = 'AuthKey_W63JQDWXV8.p8'

#     #     # settings.SOCIAL_AUTH_APPLE_PRIVATE_KEY
        
#     #     with open(private_key_path, 'rb') as f:
#     #        private_key = f.read()

#     #     client_secret = jwt.encode(
#     #         payload,
#     #         private_key, 
#     #         algorithm="ES256",
#     #         headers=headers
#     #     )
#     #     print(client_secret, 'client_secret')

#     #     # res = client_secret.decode("utf-8")

#     #     return client_secret

#     def get_client_id(self):
#         """We support multiple client_ids, but use the first one for api calls"""
#         return self.consumer_key.split(",")[0]

#     # def get_access_token(self, code, pkce_code_verifier=None):
#     #     print(code, 'code11')
#     #     url = self.access_token_url
#     #     client_secret = self.generate_client_secret()
#     #     print(client_secret, 'client_secret1')
#     #     client_id1 = 'com.lawtabby.pdf.sid'
#     #     client_secret1 = "MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgCRDgZhaN/Sspvlb7ryE8D+YChBC2uH97BvNGOKXpHxagCgYIKoZIzj0DAQehRANCAAQdUnewuWFxDIuw2Mo07NB7fmGzsY+8Proz3t87y5kJuGgCb9QPTVwusFt7q9QxVHJS0uFOn6UAGKvBAAhUAupv"

       
#     #     data = {
#     #         # "client_id": self.get_client_id(),
#     #         "client_id": client_id1,
#     #         "code": code,
#     #         "grant_type": "authorization_code",
#     #         "redirect_uri": self.callback_url,
#     #         # "redirect_uri": 'https://005d-119-155-15-151.ngrok-free.app',
#     #         "client_secret": client_secret1,
#     #     }
#     #     print(data, 'data')

        
#     #     # client_secret = 'W63JQDWXV8'
        


#     #     if pkce_code_verifier:
#     #         data["code_verifier"] = pkce_code_verifier
#     #     self._strip_empty_keys(data)
#     #     resp = requests.request(
#     #         self.access_token_method, url, data=data, headers=self.headers
#     #     )

#     #     print(resp.json(), 'access_token')
#     #     print(resp.text, 'Texc token')
#     #     access_token = None
#     #     if resp.status_code in [200, 201]:
#     #         try:
#     #             access_token = resp.json()
#     #         except ValueError:
#     #             access_token = dict(parse_qsl(resp.text))
#     #     if not access_token or "access_token" not in access_token:
#     #         raise OAuth2Error("Error retrieving access token: %s" % resp.content)
#     #     return access_token


#     def get_access_token(self, code, pkce_code_verifier=None):
#         token_endpoint = 'https://appleid.apple.com/auth/token'
#         # your_client_secret = 'eyJhbGciOiJFUzI1NiIsImtpZCI6Ilc2M0pRRFdYVjgiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJVODZLR1I1WEZVIiwiaWF0IjoxNzA0NDM3MTQyLCJleHAiOjE3MTk5ODkxNDIsImF1ZCI6Imh0dHBzOi8vYXBwbGVpZC5hcHBsZS5jb20iLCJzdWIiOiJjb20ubGF3dGFiYnkucGRmLnNpZCJ9.Kxla2m7FQ5THJaZiOxsP58eiwk4Gn8asJkWB_IyYUUquxEDQ9rTru6saCS3btBWpu35XKXXrmfNfTCtuoLbbXg'
#         your_client_id = 'com.lawtabby.pdf.sid'
#         client_secret = self.generate_client_secret()
#         print(client_secret, 'client_sec_____')

#         token_params = {
#             'grant_type': 'authorization_code',
#             'code': code,
#             'redirect_uri': 'https://377a-119-63-138-173.ngrok-free.app',
#             'client_id': your_client_id,
#             'client_secret': client_secret,
#         }

#         headers = {
#             'Content-Type': 'application/x-www-form-urlencoded',
#             'User-Agent': 'Your User Agent',
#         }

#         response = requests.post(token_endpoint, data=token_params, headers=headers)
#         print(response.text, 'response')

#         if response.status_code != 200 or 'access_token' not in response.json():
#             raise OAuth2Error("Error retrieving access token: %s" % response.content)

#         # access_token = response.json()['access_token']

#         access_token = response.json()

#         # response_content = response.text
#         # print(response_content, 'response_content')

#         # response_data = json.loads(response_content)
#         # print(response_data, 'response_data')

#         # # Access the 'access_token' from the response data
#         # access_token = response_data.get('access_token')
#         # print(access_token, 'access token')

#         # # Check if access_token is present and handle accordingly
#         # if access_token:
#         #     print(f"Access Token: {access_token}")
#         #     # Perform actions with the access token as needed
#         # else:
#         #     print("Access Token not found in the response")
#         return access_token

#     def get_redirect_url(self, authorization_url, extra_params):
#         params = {
#             "client_id": self.get_client_id(),
#             "redirect_uri": self.callback_url,
#             "response_mode": "form_post",
#             # "scope": self.scope,
#              "scope": "email name",  # Add 'email' and 'name' scopes
#             "response_type": "code id_token",
#         }
#         if self.state:
#             params["state"] = self.state
#         params.update(extra_params)
#         return "%s?%s" % (authorization_url, urlencode(params, quote_via=quote))
