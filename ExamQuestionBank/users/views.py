from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    使用自訂的 serializer 來產生包含額外資訊的 JWT token
    """
    serializer_class = CustomTokenObtainPairSerializer
