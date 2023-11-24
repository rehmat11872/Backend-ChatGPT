from allauth.socialaccount.providers.google.provider import GoogleProvider


class GoogleProviderMod(GoogleProvider):
    def extract_uid(self, data):
        return str(data['sub'])