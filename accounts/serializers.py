import json
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Contact


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        data['email'] = self.user.email
        token, created = Token.objects.get_or_create(user=self.user)
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
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.is_active = True
        user.save()
        return user



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ['id', 'name', 'avatar', 'email']
        read_only_fields = ['email']
    
    def update(self, instance, validated_data):
        # Handle avatar upload
        if 'avatar' in validated_data:
            # Delete old avatar if exists
            if instance.avatar:
                instance.avatar.delete(save=False)
        
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Add full URL for avatar if it exists
        if instance.avatar:
            request = self.context.get('request')
            if request:
                data['avatar'] = request.build_absolute_uri(instance.avatar.url)
        return data











class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
    
    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters")
        return value


class ContactResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    contact_id = serializers.IntegerField()