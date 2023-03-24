from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, View

from .models import Like, Tweet

User = get_user_model()


class HomeView(LoginRequiredMixin, ListView):  # 必ず先頭に
    model = Tweet
    template_name = "tweets/home.html"
    queryset = Tweet.objects.all().select_related("user")


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tweet = self.get_object()
        likes_count = Like.objects.filter(post=tweet).count()
        context["likes_count"] = likes_count
        context["is_like"] = Like.objects.filter(post=tweet, user=self.request.user).exists()
        return context


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Tweet
    template_name = "tweets/delete.html"
    success_url = reverse_lazy("tweets:home")

    def test_func(self):
        return self.request.user == self.get_object().user


class LikeView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Tweet, pk=pk)
        like = Like.objects.filter(post=post, user=request.user)

        if like.exists():
            return HttpResponseBadRequest("既にいいねされています")

        else:
            Like.objects.create(user=request.user, post=post)
            return redirect("tweets:detail", pk=post.pk)


class UnlikeView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(Tweet, pk=pk)

        if not Like.objects.filter(user=request.user, post=post).exists:
            return HttpResponseBadRequest("いいねされていません")

        else:
            Like.objects.filter(user=request.user, post=post).delete()
            return redirect("tweets:detail", pk=post.pk)
