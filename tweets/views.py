from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, View

from .models import Like, Tweet

User = get_user_model()


class HomeView(LoginRequiredMixin, ListView):  # 必ず先頭に
    model = Tweet
    template_name = "tweets/home.html"
    queryset = Tweet.objects.select_related("user").prefetch_related("liked_tweet")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["liked_list"] = (
            Like.objects.select_related("tweet").filter(user=self.request.user).values_list("tweet", flat=True)
        )
        # いいねしたツイートを取得
        return context


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
        likes_count = Like.objects.filter(tweet=tweet).count()
        context["likes_count"] = likes_count
        context["is_like"] = Like.objects.filter(tweet=tweet, user=self.request.user).exists()
        return context


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Tweet
    template_name = "tweets/delete.html"
    success_url = reverse_lazy("tweets:home")

    def test_func(self):
        return self.request.user == self.get_object().user


class LikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        tweet_id = self.kwargs["pk"]
        tweet = get_object_or_404(Tweet, id=tweet_id)
        Like.objects.get_or_create(tweet=tweet, user=self.request.user)
        like_url = reverse("tweets:like", kwargs={"pk": tweet_id})
        unlike_url = reverse("tweets:unlike", kwargs={"pk": tweet_id})
        like_count = tweet.liked_tweet.count()
        is_liked = True
        context = {
            "like_count": like_count,
            "tweet_id": tweet_id,
            "is_liked": is_liked,
            "like_url": like_url,
            "unlike_url": unlike_url,
        }
        return JsonResponse(context)


class UnlikeView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        tweet_id = self.kwargs["pk"]
        tweet = get_object_or_404(Tweet, pk=tweet_id)
        if like := Like.objects.filter(user=self.request.user, tweet=tweet):
            like.delete()
        is_liked = False
        like_url = reverse("tweets:like", kwargs={"pk": tweet_id})
        unlike_url = reverse("tweets:unlike", kwargs={"pk": tweet_id})
        like_count = tweet.liked_tweet.count()
        context = {
            "like_count": like_count,
            "tweet_id": tweet_id,
            "is_liked": is_liked,
            "like_url": like_url,
            "unlike_url": unlike_url,
        }
        return JsonResponse(context)
