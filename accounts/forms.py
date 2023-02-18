from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class SignUpForm(UserCreationForm):
    class Meta:
        model = User  # model = get_user_model() は NG
        fields = ("username", "email")
