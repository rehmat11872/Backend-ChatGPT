from accounts.models import User, Token, Contact
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import update_session_auth_hash
from accounts.serializers import MyTokenObtainPairSerializer, UserSerializer, ChangePasswordSerializer, UserProfileSerializer, ContactSerializer, ContactResponseSerializer
from project.settings import  GOOGLE_REDIRECT_URL, MICROSOFT_REDIRECT_URL, APPlE_REDIRECT_URL
from rest_framework import serializers
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.microsoft.views import MicrosoftGraphOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from .apple_utils import AppleOAuth2Client
from allauth.socialaccount.providers.oauth2.views import OAuth2Error
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView
from drf_spectacular.utils import extend_schema, inline_serializer
from accounts.schemas import (
    register_user_schema,
    email_verification_schema,
    change_password_schema,
    profile_get_schema,
    profile_patch_schema,
    profile_delete_schema
)


@extend_schema(tags=['Authentication'])
class UserRegistrationView(APIView):
    @register_user_schema
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'User Successfully Created'})
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class EmailVerificationAPIView(APIView):
    @email_verification_schema
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



@extend_schema(tags=['Authentication'])
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@extend_schema(tags=['Authentication'])
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @change_password_schema
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


@extend_schema(tags=['Authentication'])
class ProfileAPiView(APIView):
    permission_classes = [IsAuthenticated]
    
    @profile_get_schema
    def get(self, request):
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    
    @profile_patch_schema
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @profile_delete_schema
    def delete(self, request):
        user = request.user
        user.delete()
        return Response({'message': 'Account deleted successfully'}, status=status.HTTP_200_OK)




class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = GOOGLE_REDIRECT_URL
    client_class = OAuth2Client
    

    def post(self, request, *args, **kwargs):
        print("=" * 80)
        print("🟢 Backend - GoogleLoginView POST request received")
        print(f"🟢 Backend - Request method: {request.method}")
        print(f"🟢 Backend - Request path: {request.path}")
        print(f"🟢 Backend - Request data: {request.data}")
        print(f"🟢 Backend - GOOGLE_REDIRECT_URL from .env: {GOOGLE_REDIRECT_URL}")
        print(f"🟢 Backend - Current callback_url (before override): {self.callback_url}")
        
        # Check what frontend is sending
        if 'code' in request.data:
            print(f"🟢 Backend - Authorization code received: {request.data['code'][:50]}...")
        if 'redirect_uri' in request.data:
            frontend_redirect_uri = request.data['redirect_uri']
            print(f"🟢 Backend - Redirect URI from frontend: {frontend_redirect_uri}")
            print(f"🟢 Backend - Overriding callback_url to match frontend redirect_uri")
            # Override callback_url to use the redirect_uri from frontend
            # This is critical - the redirect_uri used in token exchange must match 
            # the one used in the initial OAuth authorization request
            self.callback_url = frontend_redirect_uri
            print(f"🟢 Backend - New callback_url: {self.callback_url}")
        else:
            print("⚠️ Backend - No redirect_uri in request.data, using default callback_url")
        
        try:
            response = super().post(request, *args, **kwargs)
            print(f"🟢 Backend - Response status: {response.status_code}")
            print(f"🟢 Backend - Response data: {response.data}")
            print("=" * 80)
            return response
        except Exception as e:
            print(f"🔴 Backend - Error in GoogleLoginView: {str(e)}")
            print(f"🔴 Backend - Error type: {type(e)}")
            import traceback
            print(f"🔴 Backend - Traceback: {traceback.format_exc()}")
            print("=" * 80)
            raise

    @property
    def username(self):
        return self.adapter.user.email
    




@extend_schema(exclude=True)
class UserRedirectView(LoginRequiredMixin, RedirectView):
    """
    This view is needed by the dj-rest-auth-library in order to work the google login. It's a bug.
    """

    permanent = False

    def get_redirect_url(self):
        return "redirect-url"



@extend_schema(exclude=True)
class MicrosoftLoginView(SocialLoginView):
    adapter_class = MicrosoftGraphOAuth2Adapter
    callback_url = MICROSOFT_REDIRECT_URL
    client_class = OAuth2Client

    @property
    def username(self):
        return self.adapter.user.email



@extend_schema(exclude=True)
class AppleLoginView(SocialLoginView):
    adapter_class = AppleOAuth2Adapter
    callback_url = APPlE_REDIRECT_URL
    client_class = AppleOAuth2Client


    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except OAuth2Error as e:
            # Handle the OAuth2Error here
            error_message = str(e)
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)

    @property
    def username(self):
        return self.adapter.user.email




@extend_schema(tags=['Authentication'])
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Delete the user's current token
            Token.objects.filter(user=request.user).delete()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)





@extend_schema(tags=['Authentication'])
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses=inline_serializer(
            name='LogoutResponse',
            fields={'message': serializers.CharField()}
        ),
        tags=['Authentication']
    )
    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
        except:
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

@extend_schema(tags=['Contact'])
class ContactView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        request=ContactSerializer,
        responses=ContactResponseSerializer,
        tags=['Contact']
    )
    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()
            return Response({
                'message': 'Thank you for contacting us! We will get back to you soon.',
                'contact_id': contact.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)