from django.contrib import admin
from django.urls import  path, include
from rest_framework_simplejwt.views import TokenVerifyView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .settings import BASE_API_V1_PREFIX

from drf_spectacular.views import(
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    # Local
    # path(f'{BASE_API_V1_PREFIX}/products/', include('products.urls')),
    path(f'{BASE_API_V1_PREFIX}/schema/', SpectacularAPIView.as_view(), name='schema'),
    path (f'{BASE_API_V1_PREFIX}/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'),name='schema-swagger-ui'),
    path(f'{BASE_API_V1_PREFIX}/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='schema-redoc'),
    path(f'{BASE_API_V1_PREFIX}/', include('company.urls')),
    path(f'{BASE_API_V1_PREFIX}/user/', include('authenticate.urls')),
    path(f'{BASE_API_V1_PREFIX}/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path(f'{BASE_API_V1_PREFIX}/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path(f'{BASE_API_V1_PREFIX}/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
