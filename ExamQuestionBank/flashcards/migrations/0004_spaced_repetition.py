# Generated manually to add spaced repetition fields and review logs
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('flashcards', '0003_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='flashcard',
            name='status',
            field=models.CharField(choices=[('learning', '學習中'), ('reviewing', '複習中'), ('mastered', '已掌握')], default='learning', max_length=20, verbose_name='狀態'),
        ),
        migrations.AddField(
            model_name='flashcard',
            name='ease_factor',
            field=models.FloatField(default=2.5, verbose_name='熟練因子'),
        ),
        migrations.AddField(
            model_name='flashcard',
            name='interval',
            field=models.IntegerField(default=1, verbose_name='間隔天數'),
        ),
        migrations.AddField(
            model_name='flashcard',
            name='repetition',
            field=models.IntegerField(default=0, verbose_name='連續成功次數'),
        ),
        migrations.AddField(
            model_name='flashcard',
            name='last_reviewed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='最後複習時間'),
        ),
        migrations.CreateModel(
            name='FlashcardReviewLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], verbose_name='表現評分')),
                ('review_interval', models.IntegerField(default=1, verbose_name='複習間隔')),
                ('reviewed_at', models.DateTimeField(auto_now_add=True, verbose_name='複習時間')),
                ('flashcard', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='review_logs', to='flashcards.flashcard', verbose_name='快閃卡')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flashcard_reviews', to=settings.AUTH_USER_MODEL, verbose_name='使用者')),
            ],
            options={
                'db_table': 'flashcard_review_logs',
                'ordering': ['-reviewed_at'],
                'verbose_name': '快閃卡複習記錄',
                'verbose_name_plural': '快閃卡複習記錄',
            },
        ),
    ]
