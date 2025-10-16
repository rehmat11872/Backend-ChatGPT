from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from accounts.serializers import UserSerializer, ChangePasswordSerializer, UserProfileSerializer

# ---------------- AUTH SCHEMAS ----------------

register_user_schema = extend_schema(
    request=UserSerializer,
    responses=inline_serializer(
        name='RegistrationResponse',
        fields={'message': serializers.CharField()}
    ),
    tags=['Authentication']
)

email_verification_schema = extend_schema(
    responses=inline_serializer(
        name='EmailVerificationResponse',
        fields={
            'message': serializers.CharField(),
            'token': serializers.CharField(),
        }
    ),
    tags=['Email']
)

change_password_schema = extend_schema(
    request=ChangePasswordSerializer,
    responses=inline_serializer(
        name='ChangePasswordResponse',
        fields={
            'message': serializers.CharField(),
            'error': serializers.CharField(required=False),
        }
    ),
    tags=['Authentication']
)

profile_get_schema = extend_schema(
    responses=UserProfileSerializer,
    tags=['Authentication']
)

profile_patch_schema = extend_schema(
    request=UserProfileSerializer,
    responses=UserProfileSerializer,
    tags=['Authentication']
)

profile_delete_schema = extend_schema(
    responses=inline_serializer(
        name='DeleteProfileResponse',
        fields={'message': serializers.CharField()}
    ),
    tags=['Authentication']
)
