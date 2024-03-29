from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"
urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("<str:username>/", views.UserProfileView.as_view(), name="profile"),
    path("<str:username>/follow/", views.FollowView.as_view(), name="follow"),
    path("<str:username>/unfollow/", views.UnFollowView.as_view(), name="unfollow"),
    path("<str:username>/following_list/", views.FollowingListView.as_view(), name="following_list"),
    path("<str:username>/follower_list/", views.FollowerListView.as_view(), name="follower_list"),
]
