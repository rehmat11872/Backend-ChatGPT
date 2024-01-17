import datetime
from rest_framework import serializers
from accounts.models import SubscriptionPlan



class PaymentSerializer(serializers.Serializer):
    amount = serializers.IntegerField()


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'
