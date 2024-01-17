from django.urls import path
# from .views import PaymentAPI
from . import views



urlpatterns = [
    path('subscription_list/', views.SubscriptionPlanList.as_view(), name='subscription_list'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe-webhook'),
    path('create_checkout_session/<pk>/', views.CreateCheckoutSessionAPIView.as_view()),
    path('simple_checkout/', views.SimpleCheckoutView, name='simple_checkout'),
    path('create_order/', views.CreateOrderView.as_view(), name='create-order'),
    path('capture_order/<str:order_id>/', views.CaptureOrderView.as_view(), name='capture-order'),

    path('webhooks/paypal/', views.ProcessWebhookView.as_view(), name='webhook_view')

    # path('stripe_payment/', PaymentAPI.as_view(), name='stripe_payment')
    # path('create-payment-intent/<pk>/', views.StripeIntentView.as_view(), name='create-payment-intent'),
    # path('cancel/', views.CancelView.as_view(), name='cancel'),
    # path('success/', views.SuccessView.as_view(), name='success'),
    # path('landing/', views.ProductLandingPageView.as_view(), name='landing-page'),
    # path('create-checkout-session/<pk>/', views.CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
]