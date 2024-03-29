from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, View

from tweets.models import Like, Tweet

from .forms import LoginForm, SignupForm
from .models import Friendship

User = get_user_model()


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class LoginView(auth_views.LoginView):
    form_class = LoginForm  # Forms.pyのクラス
    template_name = "accounts/login.html"  # 実際に表示されるファイル
    # form_classにform.pyで定義したLoginFormを指定することで、ログイン処理時にLoginFormで定義したフォームデザインが適用される。


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/profile.html"
    slug_field = "username"  # URLの末尾を指定
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        context["tweet_list"] = Tweet.objects.select_related("user").filter(user=user)  # TweetCreateViewで作ったツイートの一覧を作成
        context["following"] = Friendship.objects.filter(follower=user).count()
        context["follower"] = Friendship.objects.filter(following=user).count()
        context["is_following"] = Friendship.objects.filter(following=user, follower=self.request.user).exists()
        context["liked_list"] = (
            Like.objects.select_related("tweet").filter(user=self.request.user).values_list("tweet", flat=True)
        )
        return context


class FollowView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        follower = self.request.user
        following = get_object_or_404(User, username=self.kwargs["username"])

        if follower == following:
            return HttpResponseBadRequest("自分自身をフォローすることはできません")

        if Friendship.objects.filter(follower=follower, following=following).exists():
            messages.warning(request, "あなたはすでに{}をフォローしています".format(following.username))
            return redirect("tweets:home")

        else:
            Friendship.objects.create(follower=follower, following=following)
            messages.success(request, "{}をフォローしました".format(following.username))
            return redirect("tweets:home")


class UnFollowView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        follower = self.request.user
        following = get_object_or_404(User, username=self.kwargs["username"])

        if follower == following:
            return HttpResponseBadRequest("自分自身のフォローを外せません")

        else:
            friendship = Friendship.objects.filter(follower=follower, following=following)
            friendship.delete()
            messages.success(request, "{}のフォローを外しました".format(following.username))
            return redirect("tweets:home")


class FollowerListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "accounts/follower_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs["username"])
        context["follower_list"] = Friendship.objects.select_related("follower").filter(following=user)
        return context


class FollowingListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "accounts/following_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs["username"])
        context["following_list"] = Friendship.objects.select_related("following").filter(follower=user)
        return context
