from django.urls import path, re_path

from .views import CategoryListView, ProductRetrieveView

urlpatterns = [
    path("category", CategoryListView.as_view()),
    re_path("^product/(?P<pk>.+)/$", ProductRetrieveView.as_view())
]
