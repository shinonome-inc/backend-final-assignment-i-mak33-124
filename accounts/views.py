from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import LoginForm, SignupForm  # 指定の仕方が分からない


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class UserLoginView(LoginView):
    form_class = LoginForm  # Forms.pyのクラス
    template_name = "accounts/login.html"  # 実際に表示されるファイル
    # form_classにform.pyで定義したLoginFormを指定することで、ログイン処理時にLoginFormで定義したフォームデザインが適用される。


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"
