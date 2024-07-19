from django.urls import path, re_path

from .views import (CategoryListView, ProductRetrieveView,
                    ProductListView)

urlpatterns = [
    path("categories", CategoryListView.as_view()),
    re_path("^product/(?P<pk>.+)/$", ProductRetrieveView.as_view()),
    path("products", ProductListView.as_view())
]
