# Generated by Django 4.1.4 on 2023-04-24 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='evidence',
            field=models.FileField(blank=True, null=True, upload_to='evidence/%Y-%m-%d'),
        ),
    ]
