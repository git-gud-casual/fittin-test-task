from django.urls import path

from .decorated_jwt_views import (
    DecoratedTokenRefreshView,
    DecoratedTokenObtainPairView
)

urlpatterns = [
    path('token/', DecoratedTokenObtainPairView.as_view()),
    path('token/refresh', DecoratedTokenRefreshView.as_view()),
]
