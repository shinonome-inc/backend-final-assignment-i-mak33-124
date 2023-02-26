from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Tweet

User = get_user_model()


class TestHomeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(user=self.user, content="test_tweet")

    def test_success_get(self):
        response = self.client.get(reverse("tweets:home"))
        tweets = response.context["tweet_list"]
        self.assertEqual(tweets.count(), Tweet.objects.all().count())  # レコード数が一致するかどうか
        self.assertEqual(
            tweets.first().created_time_date, Tweet.objects.first().created_time_date
        )


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

    def test_success_get(self):
        response = self.client.get(reverse("tweets:create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/create.html")

    def test_success_post(self):
        tweet = {"content": "testtweet"}
        response = self.client.post(
            reverse("tweets:create"), test_tweet={"content": "testtweet"}
        )

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(Tweet.objects.filter(content=tweet["content"]).exists())

    def test_failure_post_with_empty_content(self):
        empty_content_tweet = {"content": ""}
        response = self.client.post(self.url, empty_content_tweet)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["content"], ["このフィールドは必須です。"])
        self.assertFalse(Tweet.objects.exists())

    def test_failure_post_with_too_long_content(self):
        long_content_tweet = {"content": "r*500"}
        response = self.client.post(self.url, long_content_tweet)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(
            form.errors["content"], ["この値は 140 文字以下でなければなりません(500文字になっています)。"]
        )
        self.assertFalse(Tweet.objects.exists())


class TestTweetDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.tweet = Tweet.objects.create(user=self.user, content="test")
        self.client.login(username="testuser", password="testpassword")

    def test_success_get(self):
        response = self.client.get(
            reverse("tweets:detail", kwargs={"pk": self.tweet.pk})
        )


# class TestTweetDeleteView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_incorrect_user(self):


# class TestFavoriteView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_favorited_tweet(self):


# class TestUnfavoriteView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_unfavorited_tweet(self):
