# Generated manually for AI chat history

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('question_bank', '0004_alter_examquestion_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIChatHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(verbose_name='使用者訊息')),
                ('response', models.TextField(verbose_name='AI 回應')),
                ('context_type', models.CharField(blank=True, max_length=50, null=True, verbose_name='上下文類型')),
                ('context_id', models.IntegerField(blank=True, null=True, verbose_name='上下文ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_chat_history', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'AI 聊天記錄',
                'verbose_name_plural': 'AI 聊天記錄',
                'db_table': 'ai_chat_history',
                'ordering': ['-created_at'],
            },
        ),
    ]
