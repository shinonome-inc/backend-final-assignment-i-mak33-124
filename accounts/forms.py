from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class SignupForm(UserCreationForm):
    class Meta:
        model = User  # model = get_user_model() は NG
        fields = ("username", "email")


class LoginForm(AuthenticationForm):  # ユーザー名とパスワードで認証する画面を作れる
    def __init__(
        self, *args, **kwargs
    ):  # *でタプル型、**辞書型として値を受け取れる、__init__はクラスを書いた時に実行される
        super().__init__(*args, **kwargs)  # super()は継承の際に用いる
        for field in self.fields.values():
            field.widget.attrs[
                "class"
            ] = "form-control"  # attrs["class"]でHTMLのクラス属性を指定、widgetは見た目をよくする
            field.widget.attrs["placeholder"] = field.label  # 入力フォームにフォーム名が表示されるように指定
