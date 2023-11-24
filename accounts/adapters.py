from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from google.auth.transport import requests
from google.oauth2 import id_token

from .providers import GoogleProviderMod


class GoogleOAuth2AdapterIdToken(GoogleOAuth2Adapter):
    provider_id = GoogleProviderMod.id

    def complete_login(self, request, app, token, **kwargs):
        idinfo = id_token.verify_oauth2_token(token.token, requests.Request(), app.client_id)
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Wrong issuer.")
        extra_data = idinfo
        login = self.get_provider().sociallogin_from_response(request, extra_data)
        return login