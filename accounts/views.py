from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin  # ログイン時のみ表示するようにする
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import LoginForm, SignupForm  # 指定の仕方が分からない


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("tweets:home")  # ?

    def form_valid(self, form):
        response = super().form_valid(form)  # ?
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class Login(LoginRequiredMixin, LoginView):  # 必ず先頭に
    form_class = LoginForm  # Forms.pyのクラス(login,logoutはまだ未実装)
    template_name = "accounts/login.html"  # 実際に表示されるファイル


# form_classにform.pyで定義したLoginFormを指定することで、ログイン処理時にLoginFormで定義したフォームデザインが適用される。


class Logout(LogoutView):  # form_classは不要
    template_name = "accounts/login.html"  # そのままでいいのか？


# 要件によるとuserprifileも追加する必要あり
