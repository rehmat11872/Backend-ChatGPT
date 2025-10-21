import json
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, SubscriptionPlan, Subscription
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



class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'duration', 'price', 'free_trial']


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    is_free_trial = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'id',
            'plan',
            'start_date',
            'end_date',
            'is_active',
            'is_free_trial',
        ]

    def get_is_free_trial(self, obj):
        return bool(obj.plan and obj.plan.free_trial)


class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)
    subscription = SubscriptionSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'avatar', 'email', 'subscription']
        read_only_fields = ['email']

    def update(self, instance, validated_data):
        # Handle avatar upload
        if 'avatar' in validated_data:
            if instance.avatar:
                instance.avatar.delete(save=False)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.avatar:
            request = self.context.get('request')
            if request:
                data['avatar'] = request.build_absolute_uri(instance.avatar.url)
        return data



# class UserProfileSerializer(serializers.ModelSerializer):
#     avatar = serializers.ImageField(required=False)
    
#     class Meta:
#         model = User
#         fields = ['id', 'name', 'avatar', 'email']
#         read_only_fields = ['email']
    
#     def update(self, instance, validated_data):
#         # Handle avatar upload
#         if 'avatar' in validated_data:
#             # Delete old avatar if exists
#             if instance.avatar:
#                 instance.avatar.delete(save=False)
        
#         return super().update(instance, validated_data)
    
#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         # Add full URL for avatar if it exists
#         if instance.avatar:
#             request = self.context.get('request')
#             if request:
#                 data['avatar'] = request.build_absolute_uri(instance.avatar.url)
#         return data









