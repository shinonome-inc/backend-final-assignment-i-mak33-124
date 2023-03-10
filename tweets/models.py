from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 1対多のリレーション
    content = models.TextField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)  # モデルの保存時に時刻・日付を保存

    def __str__(self):
        return self.content  # 管理画面でデータの判別をしやすくする(つけないと中身の判別ができない)
