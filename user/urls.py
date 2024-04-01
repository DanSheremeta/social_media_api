from django.urls import path

from user.views import (
    CreateTokenView,
    CreateUserView,
    ManageUserView,
    UserListView,
    LogoutUserView,
)

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("login/", CreateTokenView.as_view(), name="login"),
    path("logout/", LogoutUserView.as_view(), name="logout"),
    path("list/", UserListView.as_view(), name="list"),
    path("<int:pk>/", ManageUserView.as_view(), name="manage"),
]

app_name = "user"
