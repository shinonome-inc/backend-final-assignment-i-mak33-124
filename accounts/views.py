from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from tweets.models import Tweet
from .forms import LoginForm, SignupForm

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
        context["tweet_list"] = Tweet.objects.select_related("user").filter(
            user=user
        )  # TweetCreateViewで作ったツイートの一覧を作成
        return context
