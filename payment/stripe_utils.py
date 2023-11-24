import stripe
from rest_framework import status

def stripe_card_payment(data_dict):
    try:
        stripe.api_key = 'sk_test_51JeDolGB4JYTbuORxnM5WwmuRGHf9KN7LSGnNAkd0D3sGymHhLeOxjFJa1JYemWs08oKdzFMW3VDybh3GFjUrRGu00h5c89flE'
        card_details = {
            "type": "card",
            "card": {
                "number": data_dict['card_number'],
                "exp_month": data_dict['expiry_month'],
                "exp_year": data_dict['expiry_year'],
                "cvc": data_dict['cvc'],
            },
        }

        # Create a PaymentMethod using the card details
        payment_method = stripe.PaymentMethod.create(
            type='card',
            card={
                'number': card_details['card']['number'],
                'exp_month': card_details['card']['exp_month'],
                'exp_year': card_details['card']['exp_year'],
                'cvc': card_details['card']['cvc'],
            },
        )

        # You can also get the amount from the database by creating a model
        payment_intent = stripe.PaymentIntent.create(
            amount=10000,
            currency='inr',
            payment_method=payment_method.id,  # Use the PaymentMethod ID here
        )

        payment_intent_modified = stripe.PaymentIntent.modify(
            payment_intent['id'],
            payment_method=payment_method.id,
        )

        try:
            payment_confirm = stripe.PaymentIntent.confirm(
                payment_intent['id']
            )
            payment_intent_modified = stripe.PaymentIntent.retrieve(payment_intent['id'])
        except stripe.error.StripeError as e:
            payment_intent_modified = stripe.PaymentIntent.retrieve(payment_intent['id'])
            payment_confirm = {
                "stripe_payment_error": "Failed",
                "code": payment_intent_modified.get('last_payment_error', {}).get('code', ''),
                "message": payment_intent_modified.get('last_payment_error', {}).get('message', ''),
                'status': "Failed"
            }

        if payment_intent_modified and payment_intent_modified['status'] == 'succeeded':
            response = {
                'message': "Card Payment Success",
                'status': status.HTTP_200_OK,
                "card_details": card_details,
                "payment_intent": payment_intent_modified,
                "payment_confirm": payment_confirm
            }
        else:
            response = {
                'message': "Card Payment Failed",
                'status': status.HTTP_400_BAD_REQUEST,
                "card_details": card_details,
                "payment_intent": payment_intent_modified,
                "payment_confirm": payment_confirm
            }
    except stripe.error.CardError as e:
        print(f"Stripe CardError: {e}")
        response = {
            'error': "Your card number is incorrect",
            'status': status.HTTP_400_BAD_REQUEST,
            "payment_intent": {"id": "Null"},
            "payment_confirm": {'status': "Failed"}
        }
    return response


# def stripe_card_payment(data_dict):
#     try:
#         card_details = {
#             "type": "card",
#             "card": {
#                 "number": data_dict['card_number'],
#                 "exp_month": data_dict['expiry_month'],
#                 "exp_year": data_dict['expiry_year'],
#                 "cvc": data_dict['cvc'],
#             },
#         }
#         # You can also get the amount from the database by creating a model
#         payment_intent = stripe.PaymentIntent.create(
#             amount=10000,
#             currency='inr',
#         )
#         payment_intent_modified = stripe.PaymentIntent.modify(
#             payment_intent['id'],
#             payment_method=card_details['id'],
#         )
#         try:
#             payment_confirm = stripe.PaymentIntent.confirm(
#                 payment_intent['id']
#             )
#             payment_intent_modified = stripe.PaymentIntent.retrieve(payment_intent['id'])
#         except stripe.error.StripeError as e:
#             payment_intent_modified = stripe.PaymentIntent.retrieve(payment_intent['id'])
#             payment_confirm = {
#                 "stripe_payment_error": "Failed",
#                 "code": payment_intent_modified.get('last_payment_error', {}).get('code', ''),
#                 "message": payment_intent_modified.get('last_payment_error', {}).get('message', ''),
#                 'status': "Failed"
#             }
#         if payment_intent_modified and payment_intent_modified['status'] == 'succeeded':
#             response = {
#                 'message': "Card Payment Success",
#                 'status': status.HTTP_200_OK,
#                 "card_details": card_details,
#                 "payment_intent": payment_intent_modified,
#                 "payment_confirm": payment_confirm
#             }
#         else:
#             response = {
#                 'message': "Card Payment Failed",
#                 'status': status.HTTP_400_BAD_REQUEST,
#                 "card_details": card_details,
#                 "payment_intent": payment_intent_modified,
#                 "payment_confirm": payment_confirm
#             }
#     except stripe.error.CardError as e:
#         response = {
#             'error': "Your card number is incorrect",
#             'status': status.HTTP_400_BAD_REQUEST,
#             "payment_intent": {"id": "Null"},
#             "payment_confirm": {'status': "Failed"}
#         }
#     return response
