# Generated by Django 5.1.6 on 2025-04-20 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CareerConversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(max_length=100)),
                ('user_message', models.TextField()),
                ('bot_response', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
