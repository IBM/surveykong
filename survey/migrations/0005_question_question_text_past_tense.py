# Generated by Django 3.2.5 on 2021-10-25 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0004_auto_20211025_1655'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='question_text_past_tense',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
