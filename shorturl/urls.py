from .views import *
from django.urls import path
from .views import RegisterView, ShortenURLView, RedirectURLView, AdminURLListView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("shorten/", ShortenURLView.as_view(), name="shorten-url"),
    path("admin/list/", AdminURLListView.as_view(), name="admin-url-list"),
    path("redirect/<str:short_code>/", RedirectURLView.as_view(), name="redirect"),
]