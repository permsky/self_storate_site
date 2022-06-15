# Generated by Django 3.2.13 on 2022-06-15 12:25

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Box',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('in_use', models.BooleanField()),
                ('tariff', models.PositiveIntegerField(verbose_name='Цена аренды в месяц')),
            ],
        ),
        migrations.CreateModel(
            name='BoxPlace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название боксангара')),
                ('address', models.CharField(max_length=100, verbose_name='Адрес')),
                ('boxes_quantity', models.PositiveIntegerField(default=1, verbose_name='Общее количество боксов')),
                ('note', models.CharField(blank=True, max_length=100, verbose_name='Пимечание')),
            ],
        ),
        migrations.CreateModel(
            name='BoxVolume',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('volume', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Объем бокса')),
            ],
        ),
        migrations.CreateModel(
            name='RentalTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_intervals', models.PositiveIntegerField(verbose_name='Тариф в месяцах')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(auto_now_add=True, verbose_name='заказ от')),
                ('end_date', models.DateTimeField(verbose_name='заказ до')),
                ('key', models.PositiveIntegerField(verbose_name='Ключ доступа')),
                ('box', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='box_orders', to='starage_manager.box')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users_orders', to=settings.AUTH_USER_MODEL)),
                ('rental_time', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='starage_manager.rentaltime')),
            ],
        ),
        migrations.AddField(
            model_name='box',
            name='box_volume',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='boxes', to='starage_manager.boxvolume'),
        ),
        migrations.AddField(
            model_name='box',
            name='boxes_place',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='place_boxes', to='starage_manager.boxplace', verbose_name='Где находится'),
        ),
    ]
