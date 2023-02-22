from django.contrib.auth.mixins import LoginRequiredMixin  # ログイン時のみ表示するようにする
from django.views.generic import TemplateView


class HomeView(LoginRequiredMixin, TemplateView):  # 必ず先頭に
    template_name = "tweets/home.html"
