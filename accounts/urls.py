from django.urls import path, include
from accounts import views

urlpatterns = [
    path('login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', views.UserRegistrationView.as_view(), name='user-registration'),
    path('verify_email/<str:verification_code>/', views.EmailVerificationAPIView.as_view(), name='email-verification'),
    path('change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('profile/', views.ProfileAPiView.as_view(), name='profile'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path("dj-rest-auth/google/login/", views.GoogleLoginView.as_view(), name="google_login"),
    path("~redirect/", views.UserRedirectView.as_view(), name="redirect"),
    path("dj-rest-auth/microsoft/login/", views.MicrosoftLoginView.as_view(), name="microsoft_login"),
    path("dj-rest-auth/apple/login/", views.AppleLoginView.as_view(), name="apple_login"),


]