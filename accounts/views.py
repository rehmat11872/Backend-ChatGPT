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



from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter

class AppleLoginView(SocialLoginView):
    adapter_class = MicrosoftGraphOAuth2Adapter
    callback_url = APPlE_REDIRECT_URL
    client_class = OAuth2Client

    @property
    def username(self):
        return self.adapter.user.email
    