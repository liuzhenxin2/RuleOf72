# Generated by Django 2.2.13 on 2020-10-04 03:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0008_auto_20201003_0937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='price',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
