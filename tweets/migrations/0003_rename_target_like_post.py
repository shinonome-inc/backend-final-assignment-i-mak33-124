# Generated by Django 4.1.7 on 2023-03-19 06:31

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tweets", "0002_like"),
    ]

    operations = [
        migrations.RenameField(
            model_name="like",
            old_name="target",
            new_name="post",
        ),
    ]
