from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('question_bank', '0005_aichathistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='difficulty',
            field=models.CharField(
                choices=[('easy', '容易'), ('medium', '中等'), ('hard', '困難')],
                default='medium',
                max_length=20,
                verbose_name='難度',
            ),
        ),
        migrations.AddField(
            model_name='question',
            name='question_type',
            field=models.CharField(
                choices=[('選擇題', '選擇題'), ('多選題', '多選題'), ('是非題', '是非題'), ('申論題', '申論題')],
                default='選擇題',
                max_length=20,
                verbose_name='題型',
            ),
        ),
        migrations.AddIndex(
            model_name='question',
            index=models.Index(fields=['question_type'], name='question_question_7a6c62_idx'),
        ),
        migrations.AddIndex(
            model_name='question',
            index=models.Index(fields=['difficulty'], name='question_difficulty_c4d86f_idx'),
        ),
    ]
