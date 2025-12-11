from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomTokenObtainPairSerializer, UserRegisterSerializer, UserSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    使用自訂的 serializer 來產生包含額外資訊的 JWT token
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserRegisterView(generics.CreateAPIView):
    """
    使用者註冊 API

    POST /api/v1/auth/register/
    {
        "username": "string",
        "email": "string",
        "password": "string",
        "password_confirm": "string"
    }
    """
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 註冊成功後自動產生 token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # 添加自訂欄位到 token（與登入一致）
        refresh['username'] = user.username
        refresh['email'] = user.email
        refresh['is_staff'] = user.is_staff
        refresh['is_superuser'] = user.is_superuser

        return Response({
            'message': '註冊成功',
            'user': UserSerializer(user).data,
            'access': access_token,
            'refresh': str(refresh)
        }, status=status.HTTP_201_CREATED)


class CurrentUserView(APIView):
    """
    取得當前登入使用者資訊 API

    GET /api/v1/auth/me/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
