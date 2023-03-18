from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.contrib.messages import get_messages

# from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from tweets.models import Tweet

from .models import Friendship

User = get_user_model()


class TestSignupView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(User.objects.filter(username=valid_data["username"]).exists())
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        invalid_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"], email=invalid_data["email"]).exists())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username"], ["このフィールドは必須です。"])
        self.assertEqual(form.errors["email"], ["このフィールドは必須です。"])
        self.assertEqual(form.errors["password1"], ["このフィールドは必須です。"])
        self.assertEqual(form.errors["password2"], ["このフィールドは必須です。"])

    def test_failure_post_with_empty_username(self):
        empty_username_data = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, empty_username_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=empty_username_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username"], ["このフィールドは必須です。"])

    def test_failure_post_with_empty_email(self):
        data = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=data["email"]).exists())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"], ["このフィールドは必須です。"])

    def test_failure_post_with_empty_password(self):
        empty_password_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, empty_password_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=empty_password_data["password1"]).exists())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password1"], ["このフィールドは必須です。"])
        self.assertEqual(form.errors["password2"], ["このフィールドは必須です。"])

    def test_failure_post_with_duplicated_user(self):
        duplicated_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpassword",
        )

        response = self.client.post(self.url, duplicated_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username"], ["同じユーザー名が既に登録済みです。"])

    def test_failure_post_with_invalid_email(self):
        invalid_email_data = {
            "username": "testuser",
            "email": "testtest.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_email_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"], ["有効なメールアドレスを入力してください。"])

    def test_failure_post_with_too_short_password(self):
        too_short_password_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "te",
            "password2": "te",
        }
        response = self.client.post(self.url, too_short_password_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password2"], ["このパスワードは短すぎます。最低 8 文字以上必要です。"])

    def test_failure_post_with_password_similar_to_username(self):
        similar_to_username_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testuser",
            "password2": "testuser",
        }
        response = self.client.post(self.url, similar_to_username_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password2"], ["このパスワードは ユーザー名 と似すぎています。"])

    def test_failure_post_with_only_numbers_password(self):
        numbers_password_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "12345678",
            "password2": "12345678",
        }
        response = self.client.post(self.url, numbers_password_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password2"], ["このパスワードは一般的すぎます。", "このパスワードは数字しか使われていません。"])

    def test_failure_post_with_mismatch_password(self):
        mismatch_password_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassworld",
        }
        response = self.client.post(self.url, mismatch_password_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password2"], ["確認用パスワードが一致しません。"])


class TestLoginView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpassword",
        )
        self.url = reverse("accounts:login")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_success_post(self):
        test_success_data = {
            "username": "testuser",
            "password": "testpassword",
        }

        response = self.client.post(self.url, test_success_data)

        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        not_exists_data = {
            "username": "noexistuser",
            "password": "testpassword",
        }

        response = self.client.post(self.url, not_exists_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn(
            "正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。",
            form.errors["__all__"],
        )
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_password(self):
        empty_password_data = {
            "username": "testuser",
            "password": "",
        }
        response = self.client.post(self.url, empty_password_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password"], ["このフィールドは必須です。"])
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestLogoutView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        self.client.login(username="testuser", password="testpassword")

    def test_success_post(self):
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(
            response,
            reverse(settings.LOGOUT_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def test_success_get(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword")
        self.client.login(username="testuser1", password="testpassword")
        self.objects = Tweet.objects.create(user=self.user1, content="test")
        Friendship.objects.create(following=self.user2, follower=self.user1)
        response = self.client.get(reverse("accounts:profile", kwargs={"username": self.user1.username}))
        tweets = response.context["tweet_list"]
        self.assertEqual(tweets.count(), Tweet.objects.all().count())  # レコード数が一致するかどうか
        tweets_views = tweets.order_by("created_at")
        Tweet_model = Tweet.objects.order_by("created_at")
        self.assertEqual(tweets_views.first(), Tweet_model.first())  # 昇順に並び替える
        self.assertEquals(
            response.context["following"],
            Friendship.objects.filter(follower=self.user1).count(),
        )

        self.assertEquals(
            response.context["follower"],
            Friendship.objects.filter(following=self.user1).count(),
        )


class TestUserProfileEditView(TestCase):
    def test_success_get(self):
        pass

    def test_success_post(self):
        pass

    def test_failure_post_with_not_exists_user(self):
        pass

    def test_failure_post_with_incorrect_user(self):
        pass


class TestFollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword")
        self.client.login(username="testuser1", password="testpassword")

    def test_success_post(self):
        response = self.client.post(reverse("accounts:follow", kwargs={"username": self.user2.username}))
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(Friendship.objects.filter(follower=self.user1, following=self.user2).exists())

    def test_failure_post_with_not_exist_user(self):
        response = self.client.post(reverse("accounts:follow", kwargs={"username": "empty.user"}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Friendship.objects.count(), 0)

    def test_failure_post_with_self(self):
        response = self.client.post(reverse("accounts:follow", kwargs={"username": self.user1.username}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Friendship.objects.count(), 0)

    def test_post_with_existing_Friendship(self):
        Friendship.objects.create(follower=self.user1, following=self.user2)
        response = self.client.post(reverse("accounts:follow", kwargs={"username": self.user2.username}))
        messages = list(
            get_messages(response.wsgi_request)
        )  # リクエストの内容がresponse.wsgi_requestに収納される　https://qiita.com/i05tream/items/45cfd5e269cf8b2cef54
        message = str(messages[0])
        self.assertEqual(message, f"あなたはすでに{self.user2.username}をフォローしています")  # フォーマットのやり方が悪かった、Hasegawaさんのコード参照


class TestUnfollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword")
        self.client.login(username="testuser1", password="testpassword")
        Friendship.objects.create(follower=self.user1, following=self.user2)

    def test_success_post(self):
        response = self.client.post(reverse("accounts:unfollow", kwargs={"username": self.user2.username}))
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(Friendship.objects.filter(follower=self.user2, following=self.user1).exists())

    def test_failure_post_with_not_exist_user(self):
        response = self.client.post(reverse("accounts:unfollow", kwargs={"username": "not_exist_user.username"}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Friendship.objects.count(), 1)

    def test_failure_post_with_self(self):
        response = self.client.post(reverse("accounts:unfollow", kwargs={"username": self.user1.username}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Friendship.objects.count(), 1)


class TestFollowingListView(TestCase):
    def test_success_get(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("accounts:following_list", kwargs={"username": self.user.username}))
        self.assertEqual(response.status_code, 200)


class TestFollowerListView(TestCase):
    def test_success_get(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("accounts:follower_list", kwargs={"username": self.user.username}))
        self.assertEqual(response.status_code, 200)
