"""
URL configuration for ExamQuestionBank project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from rest_framework import permissions
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from users.views import CustomTokenObtainPairView, UserRegisterView, CurrentUserView


schema_view = get_schema_view(
   openapi.Info(
      title="司律考題題庫系統 API",
      default_version='v1',
      description="提供題庫、考試、快閃卡、使用者管理等功能的 RESTful API",
      contact=openapi.Contact(email="admin@exambank.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # Admin
    path('admin/', admin.site.urls),

    # Django Auth URLs (for Swagger login button - redirect to admin)
    path('accounts/login/', RedirectView.as_view(url='/admin/login/', permanent=False)),
    path('accounts/logout/', RedirectView.as_view(url='/admin/logout/', permanent=False)),

    # API Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # JWT Authentication
    path('api/v1/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/register/', UserRegisterView.as_view(), name='user_register'),
    path('api/v1/auth/me/', CurrentUserView.as_view(), name='current_user'),

   # Question Bank URLs
    path("api/v1/question_bank/", include("question_bank.urls")),
    path("api/v1/", include("question_bank.urls")),  # 也支援 /api/v1/questions/

    # Exams URLs
    path("api/v1/", include("exams.urls")),

   # Users URLs
   path('api/v1/', include('users.urls')),

   # Flashcards URLs
   path('api/v1/', include('flashcards.urls')),

   # Discussions URLs
   path('api/v1/', include('discussions.urls')),

   # Gamification URLs
   path('api/v1/', include('gamification.urls')),

   # Analytics URLs
   path('api/v1/', include('analytics.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
