import stripe
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .stripe_utils import stripe_card_payment
from django.conf import settings



class PaymentAPI(APIView):
    serializer_class = PaymentSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        amount = serializer.validated_data.get('amount')
        payment_method_id = serializer.validated_data.get('payment_method_id')

        try:
            # Set the Stripe API key
            stripe.api_key = settings.STRIPE_SECRET_KEY

            # Create a PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',  # Change to your preferred currency
                # payment_method=payment_method_id,
                payment_method="pm_card_visa",
                confirmation_method='manual',
                confirm=True,
                return_url='http://localhost:3000',

            )

            return Response({'client_secret': intent.client_secret})

        except stripe.error.CardError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
