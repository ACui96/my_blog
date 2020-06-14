# Generated by Django 2.2 on 2020-06-14 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0006_articlecolumn_likes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='articlecolumn',
            name='likes',
        ),
        migrations.AddField(
            model_name='articlepost',
            name='likes',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
