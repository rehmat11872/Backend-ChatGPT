from django.shortcuts import render
from accounts.models import User, Token
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import update_session_auth_hash
from accounts.serializers import MyTokenObtainPairSerializer, UserSerializer, ChangePasswordSerializer, UserProfileSerializer
from rest_framework import generics
from django.conf import settings
from project.settings import  GOOGLE_REDIRECT_URL, MICROSOFT_REDIRECT_URL, APPlE_REDIRECT_URL
from rest_framework import serializers, status

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     # return Response({'message': 'Please verify your email address'})
        #     return Response({'message': 'User SuccessFully Created'})
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'User Successfully Created'})
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class EmailVerificationAPIView(APIView):
    def get(self, request, verification_code):
        try:
            user = User.objects.get(email_verification_code=verification_code, is_active=False)
        except User.DoesNotExist:
            return Response({'message': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = True
        user.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'message': 'Email verified successfully',
                         'token': token.key
                         },
                        status=status.HTTP_200_OK)



class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get('old_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                update_session_auth_hash(request, user) 
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileAPiView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer 

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.filter(email=user.email)
        return queryset


from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView



class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = GOOGLE_REDIRECT_URL
    client_class = OAuth2Client
    



    @property
    def username(self):
        return self.adapter.user.email
    



from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView
class UserRedirectView(LoginRequiredMixin, RedirectView):
    """
    This view is needed by the dj-rest-auth-library in order to work the google login. It's a bug.
    """

    permanent = False

    def get_redirect_url(self):
        return "redirect-url"


from allauth.socialaccount.providers.microsoft.views import MicrosoftGraphOAuth2Adapter


class MicrosoftLoginView(SocialLoginView):
    adapter_class = MicrosoftGraphOAuth2Adapter
    callback_url = MICROSOFT_REDIRECT_URL
    client_class = OAuth2Client

    @property
    def username(self):
        return self.adapter.user.email


from allauth.socialaccount.views import SignupView
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
# from allauth.socialaccount.providers.apple.client import AppleOAuth2Client
from .apple_utils import AppleOAuth2Client

class AppleLoginView(SocialLoginView):
    adapter_class = AppleOAuth2Adapter
    callback_url = 'https://005d-119-155-15-151.ngrok-free.app'
    client_class = AppleOAuth2Client


    # def post(self, request, *args, **kwargs):
    #     print("Entering AppleLoginView post method")
    #     print(request.data, 'testing')
    #     code = request.data.get("code")
    #     print('paras_____::::', code)
    #     response = super().post(request, *args, **kwargs)
    #     print("Exiting AppleLoginView post method", response)
    #     return response

    @property
    def username(self):
        return self.adapter.user.email


import requests
from rest_framework.decorators import api_view
@api_view(['POST'])
def validate_apple_signin(request):
    if request.method == 'POST':
        client_id = 'com.lawtabby.pdf.sid'
        # client_secret = 'W63JQDWXV8'
        client_secret = "MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQgCRDgZhaN/Sspvlb7ryE8D+YChBC2uH97BvNGOKXpHxagCgYIKoZIzj0DAQehRANCAAQdUnewuWFxDIuw2Mo07NB7fmGzsY+8Proz3t87y5kJuGgCb9QPTVwusFt7q9QxVHJS0uFOn6UAGKvBAAhUAupv"
        code = request.data.get('code')  # Get the authorization code from the frontend

        # Make a POST request to Apple's token validation endpoint
        response = requests.post(
            'https://appleid.apple.com/auth/token',
            data={
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': 'https://180d-119-73-112-58.ngrok-free.app'  # Provide your redirect URI here
            }
        )

        if response.status_code == 200:
            token_data = response.json()
            print(token_data, 'paras')
            # Process the token_data (e.g., store tokens, set user as logged in, etc.)
            return Response(token_data, status=response.status_code)
        else:
            error_data = response.json()
            # Handle error response from Apple's endpoint
            return Response(error_data, status=response.status_code)




def index(request):
    return render(request, 'apple_auth/index.html')


from django.http import HttpResponseRedirect
from urllib.parse import urlencode
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def apple_sign_in(request):
    # Construct the Apple sign-in URL
    apple_auth_url = 'https://appleid.apple.com/auth/authorize'
    params = {
        'response_type': 'code',
        'response_mode': 'form_post',
        'client_id': 'com.lawtabby.pdf.sid',
        # 'redirect_uri': 'https://yourdomain.com/accounts/apple/callback',  # Replace with your redirect URL
        'redirect_uri': 'https://c8ac-119-155-15-151.ngrok-free.app/accounts/apple/callback/',  # Replace with your redirect URL
        'state': 'state',
        'scope': 'name email',
        
    }
    apple_sign_in_url = f"{apple_auth_url}?{urlencode(params)}"
    print(apple_sign_in_url, 'url11')
    return HttpResponseRedirect(apple_sign_in_url)




from django.http import HttpResponse
import json
import base64

@csrf_exempt
def apple_callback(request):
    if request.method == 'POST' and 'code' in request.POST:
        print(request.POST, 'all data')
        # received_state = request.POST.get('state')
        # expected_state = request.session.get('state')  # Retrieve the state from session

        # if received_state != expected_state:
        #     return HttpResponse('Authorization server returned an invalid state parameter')

        # Apple token endpoint URL
        token_endpoint = 'https://appleid.apple.com/auth/token'

        your_client_secret = 'eyJhbGciOiJFUzI1NiIsImtpZCI6Ilc2M0pRRFdYVjgiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJVODZLR1I1WEZVIiwiaWF0IjoxNzA0NDM3MTQyLCJleHAiOjE3MTk5ODkxNDIsImF1ZCI6Imh0dHBzOi8vYXBwbGVpZC5hcHBsZS5jb20iLCJzdWIiOiJjb20ubGF3dGFiYnkucGRmLnNpZCJ9.Kxla2m7FQ5THJaZiOxsP58eiwk4Gn8asJkWB_IyYUUquxEDQ9rTru6saCS3btBWpu35XKXXrmfNfTCtuoLbbXg'
        your_client_id = 'com.lawtabby.pdf.sid'
        # Parameters for token exchange
        token_params = {
            'grant_type': 'authorization_code',
            'code': request.POST['code'],
            'redirect_uri': 'https://c8ac-119-155-15-151.ngrok-free.app/accounts/apple/callback/',  # Replace with your redirect URL
            'client_id': your_client_id,
            'client_secret': your_client_secret,  # Retrieve this from the generated client secret
        }

        # Headers required by Apple
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Your User Agent',  # Set your user agent here
        }

        # Exchange code for tokens
        response = requests.post(token_endpoint, data=token_params, headers=headers)
        print(response.text, 'response')

        if response.status_code != 200 or 'access_token' not in response.json():
            error_msg = 'Error getting an access token: ' + response.text
            return HttpResponse(error_msg)

        access_token = response.json()['access_token']
        print(access_token, 'accession token')
        id_token = response.json().get('id_token')

        # Decode and extract information from the ID token
        if id_token:
            id_token_parts = id_token.split('.')
            claims = json.loads(base64.b64decode(id_token_parts[1] + '===').decode('utf-8'))
            # Extract required information from claims
            print(claims, 'claims')
            email = claims.get('email')  # Get the user's email

            # Use the extracted username and email as needed 
            print(f"Email: {email}")

            return render(request, 'apple_auth/callback.html', {'user_data': claims})
        else:
            return HttpResponse('ID token not found in the response')
    else:
        return HttpResponse('Invalid request')