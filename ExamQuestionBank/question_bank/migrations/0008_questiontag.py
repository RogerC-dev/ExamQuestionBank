from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("question_bank", "0007_essaygrading_essaysubmission_examseries_examsession_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="QuestionTag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="建立時間")),
                ("question", models.ForeignKey(on_delete=models.CASCADE, to="question_bank.question", verbose_name="題目")),
                ("tag", models.ForeignKey(on_delete=models.CASCADE, to="question_bank.tag", verbose_name="標籤")),
            ],
            options={
                "db_table": "question_tag",
                "verbose_name": "題目標籤",
                "verbose_name_plural": "題目標籤",
                "unique_together": {("question", "tag")},
            },
        ),
        migrations.AddField(
            model_name="question",
            name="tags",
            field=models.ManyToManyField(blank=True, related_name="questions", through="question_bank.QuestionTag", to="question_bank.tag", verbose_name="標籤"),
        ),
    ]

