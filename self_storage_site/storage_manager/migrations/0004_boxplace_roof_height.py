# Generated by Django 3.2.13 on 2022-06-17 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage_manager', '0003_auto_20220617_0615'),
    ]

    operations = [
        migrations.AddField(
            model_name='boxplace',
            name='roof_height',
            field=models.FloatField(default=3.5, verbose_name='Высота ангара'),
        ),
    ]
