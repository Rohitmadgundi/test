from django.urls import path,include
from account.views import ContactModelViewSet,SendPasswordResetEmailView, UserChangePasswordView, UserLoginView, UserProfileView, UserRegistrationView, UserPasswordResetView,Predict
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('contact',ContactModelViewSet,basename='contact')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='reset-password'),
    path('predict/', Predict.as_view(), name='predict'),
    path('contact/',include(router.urls)),
]