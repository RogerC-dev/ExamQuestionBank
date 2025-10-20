from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自訂 JWT Token，包含使用者的額外資訊
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # 添加自訂欄位
        token['username'] = user.username
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser

        return token
