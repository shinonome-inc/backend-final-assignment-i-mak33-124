from django.contrib.auth import get_user_model
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

    def test_success_post(self):
        tweet = {"content": "testtweet"}
        response = self.client.post(reverse("tweets:create"), tweet)

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(Tweet.objects.filter(content=tweet["content"]).exists())

    def test_failure_post_with_empty_content(self):
        empty_content_tweet = {"content": ""}
        response = self.client.post(reverse("tweets:create"), empty_content_tweet)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.errors["content"], ["このフィールドは必須です。"])
        self.assertFalse(Tweet.objects.exists())

    def test_failure_post_with_too_long_content(self):
        long_content_tweet = {"content": "r" * 500}
        response = self.client.post(reverse("tweets:create"), long_content_tweet)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(
            form.errors["content"], ["この値は 140 文字以下でなければなりません( 500 文字になっています)。"]
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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tweet"], self.tweet)


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser1", password="testpassword"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", password="testpassword"
        )
        self.tweet1 = Tweet.objects.create(user=self.user1, content="tweet1")
        self.tweet2 = Tweet.objects.create(user=self.user2, content="tweet2")
        self.client.login(username="testuser1", password="testpassword")

    def test_success_post(self):
        response = self.client.post(
            reverse("tweets:delete", kwargs={"pk": self.tweet1.pk})
        )
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(Tweet.objects.filter(content="tweet1").exists())

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(reverse("tweets:delete", kwargs={"pk": 500}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Tweet.objects.count(), 2)  # ツイート数を確認して削除されていないことを確認

    def test_failure_post_with_incorrect_user(self):
        response = self.client.post(
            reverse("tweets:delete", kwargs={"pk": self.tweet2.pk})
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Tweet.objects.count(), 2)


# class TestFavoriteView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_favorited_tweet(self):


# class TestUnfavoriteView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_unfavorited_tweet(self):
