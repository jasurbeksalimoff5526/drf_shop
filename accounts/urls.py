from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SignUpView, VerifyCodeView, GetNewCodeView, ChangeProfileInfoView, UploadProfilePhotoView, \
    ProfileView, ProfileUpdateView, LogoutView, LoginView, ForgotPasswordView, ResetPasswordView, ChangePasswordView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("refresh", TokenRefreshView.as_view()),
    path('signup', SignUpView.as_view()),
    path('verify', VerifyCodeView.as_view()),
    path('new-code', GetNewCodeView.as_view()),
    path("change-profile-info", ChangeProfileInfoView.as_view()),
    path("upload-photo", UploadProfilePhotoView.as_view()),
    path("profile", ProfileView.as_view()),
    path("profile/update", ProfileUpdateView.as_view()),
    path("login", LoginView.as_view()),
    path("logout", LogoutView.as_view()),
    path("forgot-password", ForgotPasswordView.as_view()),
    path("reset-password", ResetPasswordView.as_view()),
    path("change-password", ChangePasswordView.as_view()),

]


urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)


