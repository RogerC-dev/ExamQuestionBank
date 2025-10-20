# Generated manually on 2025-10-17
# Add unique constraint for (exam, order) to prevent duplicate order numbers in the same exam

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('question_bank', '0002_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='examquestion',
            unique_together={('exam', 'question'), ('exam', 'order')},
        ),
    ]
