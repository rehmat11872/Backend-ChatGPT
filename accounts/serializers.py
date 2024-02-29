import json
import random
import string
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
from .utils import send_email_verification_code


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        data['email'] = self.user.email
        token = Token.objects.get(user=self.user)
        token_to_str = str(token)
        token_to_json = json.dumps(token_to_str)
        token_to_load = json.loads(token_to_json)
        data['token'] = token_to_load
        data['message'] = 'Login successful'
        return data



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        email_verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        # user.email_verification_code = email_verification_code
        user.is_active = True
        user.save()
        # send_email_verification_code(user.email, email_verification_code)
        return user



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'avatar', 'email']









