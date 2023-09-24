# Generated by Django 4.0.3 on 2023-06-22 01:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_image', models.ImageField(upload_to='log_images/')),
                ('logged_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
