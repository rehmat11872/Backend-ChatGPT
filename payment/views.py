# import stripe
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .serializers import *
# from .stripe_utils import stripe_card_payment
# from django.conf import settings

#New
import json
import stripe
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views import View
from accounts.models import SubscriptionPlan, User, Subscription
from django.shortcuts import get_object_or_404
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from rest_framework import generics
from accounts.models import SubscriptionPlan
from .serializers import SubscriptionPlanSerializer


stripe.api_key = settings.STRIPE_SECRET_KEY



class SubscriptionPlanList(generics.ListAPIView):
    serializer_class = SubscriptionPlanSerializer

    def get_queryset(self):
        # Exclude subscription plans with duration as 'free_trial'
        return SubscriptionPlan.objects.exclude(duration='free_trial').order_by('id')

    def post(self, request):
        serializer = SubscriptionPlanSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Subscription Successfully Created'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




class CreateCheckoutSessionAPIView(APIView):
    def post(self, request, *args, **kwargs):
        subscription_id = self.kwargs["pk"]
        print(subscription_id, 'subscription_id')
        subscription = get_object_or_404(SubscriptionPlan, id=subscription_id)
        # YOUR_DOMAIN = "http://127.0.0.1:8000"
        YOUR_FRONTEND_DOMAIN = "http://localhost:5173"
        # YOUR_FRONTEND_DOMAIN = "https://ai-lawyer.neuracase.com"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': subscription.price,
                        'product_data': {
                            'name': subscription.name,
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "product_id": subscription.id
            },
            mode='payment',
            # success_url=YOUR_DOMAIN + '/payment/success/',
            success_url=YOUR_FRONTEND_DOMAIN + '/subscription?success=true',
            # cancel_url='http://localhost:5173/subscription'
            cancel_url = YOUR_FRONTEND_DOMAIN + '/subscription?canceled=true',
        )

        return Response({'id': checkout_session.id})


@csrf_exempt
def stripe_webhook(request):
  print('working')
  payload = request.body
  sig_header = request.META['HTTP_STRIPE_SIGNATURE']
  event = None

  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )
  except ValueError as e:
    # Invalid payload
    return HttpResponse(status=400)
  except stripe.error.SignatureVerificationError as e:
    # Invalid signature
    return HttpResponse(status=400)


  # Handle the checkout.session.completed event
  if event['type'] == 'checkout.session.completed' or event.type == 'payment_intent.succeeded':
    # Retrieve the session. If you require line items in the response, you may include them by expanding line_items.
    session = stripe.checkout.Session.retrieve(
      event['data']['object']['id'],
      expand=['line_items'],
    )

    customer_email = session["customer_details"]["email"]
    product_id = session["metadata"]["product_id"]

    product = SubscriptionPlan.objects.get(id=product_id)



    user = User.objects.get(email=customer_email)
    subscription = Subscription.objects.get(user=user)
    print(subscription, 'subscription11')
    subscription.plan = product
    subscription.start_date = timezone.now()
    # Set end_date based on subscription duration
    if product.duration == 'monthly':
        print(product.duration, 'ok')
        subscription.end_date = subscription.start_date + timedelta(days=30)
    elif product.duration == 'yearly':
        subscription.end_date = subscription.start_date + timedelta(days=365)
    else:
        # Handle other subscription durations accordingly
        pass
    subscription.is_active = True
    subscription.is_upgraded = True
    subscription.payment_id = session.id
    subscription.amount_paid = session["amount_total"]
    subscription.payment_status = session["payment_status"]
    subscription.save()


    send_mail(
        subject="Here is your product",
        message=f"Thanks for your purchase. Here is the product you ordered. The Package Name is {product.name}",
        recipient_list=[customer_email],
        from_email="matt@test.com"
    )



    # print(session)

    # line_items = session.line_items
    # Fulfill the purchase...
    # fulfill_order(line_items)


  return HttpResponse(status=200)



from django.shortcuts import render
def SimpleCheckoutView(request):
   return render(request, 'base/simple_checkout.html')



# class SuccessView(TemplateView):
#     template_name = "success.html"


# class CancelView(TemplateView):
#     template_name = "cancel.html"


# class ProductLandingPageView(TemplateView):
#     template_name = "landing.html"

#     def get_context_data(self, **kwargs):
#         subscription = SubscriptionPlan.objects.get(name="Basic Subsciption")
#         context = super(ProductLandingPageView, self).get_context_data(**kwargs)
#         context.update({
#             "product": subscription,
#             "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY
#         })
#         return context



# class CreateCheckoutSessionView(View):
#     def post(self, request, *args, **kwargs):
#         subscription_id = self.kwargs["pk"]
#         print(subscription_id, 'subscription_id')
#         # subscription = SubscriptionPlan.objects.get(id=subscription_id)
#         subscription = get_object_or_404(SubscriptionPlan, id=subscription_id)
#         YOUR_DOMAIN = "http://127.0.0.1:8000"

#         # if request.user.subscription and request.user.subscription.is_active:
#         #     messages.error(request, 'You already have an active subscription.')
#         #     return JsonResponse({'error': 'You already have an active subscription.'}, status=400)


#         checkout_session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=[
#                 {
#                     'price_data': {
#                         'currency': 'usd',
#                         'unit_amount': subscription.price,
#                         'product_data': {
#                             'name': subscription.name,
#                             # 'images': ['https://i.imgur.com/EHyR2nP.png'],
#                         },
#                     },
#                     'quantity': 1,
#                 },
#             ],
#             metadata={
#                 "product_id": subscription.id
#             },
#             mode='payment',
#             success_url=YOUR_DOMAIN + '/success/',
#             cancel_url=YOUR_DOMAIN + '/cancel/',
#         )
#         return JsonResponse({
#             'id': checkout_session.id
#         })


from .utils import generate_access_token
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import requests

class CreateOrderView(APIView):
    def post(self, request):
        try:
            print(request.data)
            if 'cart' in request.data:
                # The 'cart' key is present in the request data
                cart = request.data['cart']
                print(cart, 'cart')
            cart1 = request.data.get('cart')
            # Use the cart information to calculate purchase unit details
            print("Shopping cart information passed from the frontend createOrder() callback:", cart1)

            # Generate an access token for PayPal API authentication
            access_token = generate_access_token()
            print(access_token, 'access_token')

            base = "https://api-m.sandbox.paypal.com"
            url = f"{base}/v2/checkout/orders"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
            payload = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": "USD",
                            "value": "10.00",
                        },
                    },
                ],
            }

            response = requests.post(url, headers=headers, json=payload)
            print(response, 'response______')
            return Response(response.json(), status=response.status_code)

        except Exception as e:
            print(f"Failed to create order: {e}")
            return Response({"error": "Failed to create order"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CaptureOrderView(APIView):
    def post(self, request, order_id):
        try:
            # Capture payment for the created order to complete the transaction
            access_token = generate_access_token()

            base = "https://api-m.sandbox.paypal.com"
            url = f"{base}/v2/checkout/orders/{order_id}/capture"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }

            response = requests.post(url, headers=headers)
            return Response(response.json(), status=response.status_code)

        except Exception as e:
            print(f"Failed to capture order: {e}")
            return Response({"error": "Failed to capture order"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





import json

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View



@method_decorator(csrf_exempt, name="dispatch")
class ProcessWebhookView(View):
    def post(self, request):
        if "HTTP_PAYPAL_TRANSMISSION_ID" not in request.META:
            return HttpResponseBadRequest()

        auth_algo = request.META['HTTP_PAYPAL_AUTH_ALGO']
        cert_url = request.META['HTTP_PAYPAL_CERT_URL']
        transmission_id = request.META['HTTP_PAYPAL_TRANSMISSION_ID']
        transmission_sig = request.META['HTTP_PAYPAL_TRANSMISSION_SIG']
        transmission_time = request.META['HTTP_PAYPAL_TRANSMISSION_TIME']
        webhook_id = settings.PAYPAL_WEBHOOK_ID
        event_body = request.body.decode(request.encoding or "utf-8")


        webhook_event = json.loads(event_body)
        print(webhook_event, 'webhook_event')
        payment_id = webhook_event['resource']['id']
        payment_status = webhook_event['resource']['status']

        # Printing the extracted payment ID and status
        print(f"Payment ID: {payment_id}")
        print(f"Payment Status: {payment_status}")

        event_type = webhook_event["event_type"]
        print(event_type)

        if "resource" in webhook_event and "purchase_units" in webhook_event["resource"]:
            purchase_units = webhook_event["resource"]["purchase_units"]
            for unit in purchase_units:
                amount_value = unit.get("amount", {}).get("value")
                # payment_status = unit.get("status")
                # payment_id = unit.get("id")
                resource = webhook_event["resource"]
                payment_id = resource.get("id")  # Extract payment ID
                payment_status = resource.get("status")
                print("Payment ID:", payment_id)
                print("Payment Status:", payment_status)
                if "custom_id" in unit:
                    custom_data = json.loads(unit["custom_id"])
                    plan_name = custom_data.get("planName")
                    user_email = custom_data.get("userEmail")
                    print("Plan Name:", plan_name)
                    print("User Email:", user_email)
                    product = SubscriptionPlan.objects.get(id=plan_name)
                    user = User.objects.get(email=user_email)
                    subscription = Subscription.objects.get(user=user)
                    print(subscription, 'subscription11')
                    subscription.plan = product
                    subscription.start_date = timezone.now()
                    # Set end_date based on subscription duration
                    if product.duration == 'monthly':
                        print(product.duration, 'ok')
                        subscription.end_date = subscription.start_date + timedelta(days=30)
                    elif product.duration == 'yearly':
                        subscription.end_date = subscription.start_date + timedelta(days=365)
                    else:
                        # Handle other subscription durations accordingly
                        pass
                    subscription.is_active = True
                    subscription.is_upgraded = True
                    subscription.payment_id = payment_id
                    subscription.amount_paid = amount_value
                    subscription.payment_status = payment_status
                    subscription.save()

        CHECKOUT_ORDER_APPROVED = "CHECKOUT.ORDER.APPROVED"

        if event_type == CHECKOUT_ORDER_APPROVED:
            customer_email = webhook_event["resource"]["payer"]["email_address"]
            product_link = "https://justdjango.com/pricing"
            send_mail(
                subject="Your access",
                message=f"Thank you for purchasing my product. Here is the link:",
                from_email="raorehmat11@email.com",
                recipient_list=[customer_email]
            )



        return HttpResponse()
