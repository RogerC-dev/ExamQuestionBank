from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


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


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    使用者註冊 Serializer
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate_email(self, value):
        """檢查 email 是否已被使用"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("此電子郵件已被註冊")
        return value

    def validate_username(self, value):
        """檢查 username 是否已被使用"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("此使用者名稱已被使用")
        return value

    def validate(self, attrs):
        """檢查兩次密碼是否一致"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password_confirm": "兩次輸入的密碼不一致"
            })
        return attrs

    def create(self, validated_data):
        """建立使用者"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    使用者資訊 Serializer
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_staff', 'is_admin', 'date_joined')
        read_only_fields = ('id', 'date_joined')
