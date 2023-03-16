from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField()


class Friendship(models.Model):
    following = models.ForeignKey(User, related_name="follower", on_delete=models.CASCADE)
    follower = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    created_time_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} : {}".format(self.follower.username, self.following.username)
