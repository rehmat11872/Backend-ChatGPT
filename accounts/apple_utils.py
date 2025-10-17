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


