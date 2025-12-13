from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('question_bank', '0008_questiontag'),
    ]

    operations = [
        migrations.CreateModel(
            name='EssayAnalysisChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField(verbose_name='申論題目')),
                ('analysis_response', models.TextField(verbose_name='AI 解析回應')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='essay_analysis_chats', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '申論解析記錄',
                'verbose_name_plural': '申論解析記錄',
                'db_table': 'essay_analysis_chat',
                'ordering': ['-created_at'],
            },
        ),
    ]
