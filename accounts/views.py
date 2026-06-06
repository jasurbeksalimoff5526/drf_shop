from rest_framework_simplejwt.tokens import RefreshToken
from .models import VIA_EMAIL, VIA_PHONE, SELLER, ORDINARY_USER, NEW, CODE_VERIFY, CHANGE_INFO, DONE
from rest_framework.generics import CreateAPIView
from rest_framework import permissions, status
from .models import CustomUser
from shared.utils import send_to_mail
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializer import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    ResetPasswordSerializer,
    SignUpSerializer,
    VerifyCodeSerializer,
    ResendCodeSerializer,
    ChangeProfileInfoSerializer, ProfileSerializer
)



class SignUpView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignUpSerializer
    queryset = CustomUser.objects.all()


class VerifyCodeView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = VerifyCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = VerifyCodeSerializer(data=request.data )

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            verify_code = serializer.validated_data["verify_code"]

            verify_code.is_used = True
            verify_code.save()

            user.auth_status = CODE_VERIFY
            user.save()

            return Response(
                {
                    "message": "Kod muvaffaqiyatli tasdiqlandi.",
                    "auth_status": user.auth_status,
                    "tokens": user.token(),
                },
                status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetNewCodeView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResendCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = ResendCodeSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            code = user.create_code(user.auth_type)

            if user.auth_type == VIA_EMAIL:
                send_to_mail(
                    message=f"Sizning yangi tasdiqlash kodingiz: {code}",
                    email=user.email,
                )
            elif user.auth_type == VIA_PHONE:
                print(f"========={code}============")

            return Response({"message": "Yangi tasdiqlash kodi yuborildi."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeProfileInfoView(APIView):
    serializer_class = ChangeProfileInfoSerializer

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = ChangeProfileInfoSerializer(instance=user, data=request.data, partial=True, context={"request": request})

        if user.auth_status in [CHANGE_INFO, DONE]:
            return Response({"message": "Siz bu qismdan o'tib bo'lgansiz"}, status=status.HTTP_400_BAD_REQUEST)
        if user.auth_status == NEW:
            return Response({"message": "Siz avval kodni tasdiqlashingiz kerak!"}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Malumotlar muvaffaqiyatli saqlandi. Endi rasm yuklang.",
                    "auth_status": user.auth_status,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadProfilePhotoView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = ProfileUpdateSerializer

    def put(self, request, *args, **kwargs):
        user = request.user

        # if user.auth_status != CHANGE_INFO:
        #     return Response(
        #         {"message": "Siz profil malumotlarini to'ldirishingiz kerak"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProfileUpdateSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Ro'yxatdan o'tish muvaffaqiyatli yakunlandi!", "auth_status": user.auth_status, },
                status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        serializer = ProfileSerializer(request.user)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)


class ProfileUpdateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = ProfileUpdateSerializer

    def put(self, request, *args, **kwargs):
        serializer = ProfileUpdateSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            return Response({"message": "Login muvaffaqiyatli", "tokens": user.token()},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"message": "Refresh token xato"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout muvaffaqiyatli"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"refresh token xato "}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        verify_type = serializer.validated_data["verify_type"]

        code = user.create_code(verify_type)

        if verify_type == VIA_EMAIL:
            send_to_mail(
                message=f"Sizning parolni tiklash (reset) kodingiz: {code}",
                email=user.email,
            )
        else:
            print(f"========={code}===========")

        return Response({"message": "Tiklash uchun kod yuborildi."}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        verify_code = serializer.validated_data["verify_code"]
        new_password = serializer.validated_data["new_password"]

        verify_code.is_used = True
        verify_code.save()

        user.set_password(new_password)
        user.save()

        return Response({"message": "Parol muvaffaqiyatli yangilandi.", "tokens": user.token()},
                        status=status.HTTP_200_OK, )


class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        new_password = serializer.validated_data["new_password"]

        user.set_password(new_password)
        user.save()

        return Response({"message": "Parol muvaffaqiyatli o'zgartirildi."}, status=status.HTTP_200_OK)
