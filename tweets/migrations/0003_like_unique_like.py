# Generated by Django 4.1.6 on 2023-04-15 22:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tweets", "0002_like"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="like",
            constraint=models.UniqueConstraint(fields=("tweet", "user"), name="unique_like"),
        ),
    ]
