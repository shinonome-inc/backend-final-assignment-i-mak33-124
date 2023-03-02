from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from .models import Tweet


class HomeView(LoginRequiredMixin, ListView):  # 必ず先頭に
    model = Tweet
    template_name = "tweets/home.html"


class TweetCreateView(LoginRequiredMixin, CreateView):
    model = Tweet
    fields = ["content"]  # forms.pyは不要
    template_name = "tweets/create.html"
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):  # 投稿ユーザーとリクエストユーザーを紐づける,https://qiita.com/K_SIO/items/dd9f556ae57780448ef0
        form.instance.user = self.request.user
        return super().form_valid(form)


class TweetDetailView(LoginRequiredMixin, DetailView):
    model = Tweet
    template_name = "tweets/detail.html"
    context_object_name = "tweet"


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Tweet
    template_name = "tweets/delete.html"
    success_url = reverse_lazy("tweets:home")

    def test_func(self):
        return self.request.user == self.get_object().user
