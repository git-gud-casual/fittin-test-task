from django.urls import path

from .views import CartViewSet


urlpatterns = [
    path("cart", CartViewSet.as_view({"get": "list", "post": "create"})),
    path("cart/<int:product_id>/<str:size>", CartViewSet.as_view({"put": "update", "delete": "destroy"})),
]
