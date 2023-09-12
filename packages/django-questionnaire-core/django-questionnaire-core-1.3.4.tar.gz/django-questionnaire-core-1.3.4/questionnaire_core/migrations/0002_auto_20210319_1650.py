from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("questionnaire_core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="answerfile",
            name="order",
            field=models.PositiveIntegerField(db_index=True, editable=False, verbose_name="order"),
        ),
        migrations.AlterField(
            model_name="question",
            name="order",
            field=models.PositiveIntegerField(db_index=True, editable=False, verbose_name="order"),
        ),
        migrations.AlterField(
            model_name="questionanswer",
            name="order",
            field=models.PositiveIntegerField(db_index=True, editable=False, verbose_name="order"),
        ),
    ]
