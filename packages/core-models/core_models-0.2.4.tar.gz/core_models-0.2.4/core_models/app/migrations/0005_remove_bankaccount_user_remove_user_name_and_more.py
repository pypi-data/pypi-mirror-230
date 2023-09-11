# Generated by Django 4.2 on 2023-04-26 06:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_user_reset_token_user_reset_token_expiry'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bankaccount',
            name='user',
        ),
        migrations.RemoveField(
            model_name='user',
            name='name',
        ),
        migrations.AddField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
        migrations.AddField(
            model_name='user',
            name='job_role',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='last name'),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('deleted', models.BooleanField(default=False)),
                ('deleted_by_id', models.UUIDField(blank=True, null=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notice_type', models.CharField(max_length=50)),
                ('object_id', models.UUIDField(blank=True, null=True)),
                ('seen', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
    ]
