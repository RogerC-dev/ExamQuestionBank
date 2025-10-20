# Generated manually on 2025-10-17
# Change order field from PositiveIntegerField to IntegerField to support negative numbers as temporary placeholders

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('question_bank', '0003_add_exam_order_unique_constraint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examquestion',
            name='order',
            field=models.IntegerField(verbose_name='題目順序'),
        ),
    ]
