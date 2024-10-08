# Generated by Django 5.1 on 2024-09-05 08:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestione', '0009_show_cover'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='seats_count',
        ),
        migrations.RemoveField(
            model_name='booking',
            name='seats_type',
        ),
        migrations.RemoveField(
            model_name='show',
            name='free_seats_palco1',
        ),
        migrations.RemoveField(
            model_name='show',
            name='free_seats_palco2',
        ),
        migrations.RemoveField(
            model_name='show',
            name='free_seats_palco3',
        ),
        migrations.RemoveField(
            model_name='show',
            name='free_seats_palco4',
        ),
        migrations.RemoveField(
            model_name='show',
            name='free_seats_platea',
        ),
        migrations.RemoveField(
            model_name='show',
            name='seats_palco1',
        ),
        migrations.RemoveField(
            model_name='show',
            name='seats_palco2',
        ),
        migrations.RemoveField(
            model_name='show',
            name='seats_palco3',
        ),
        migrations.RemoveField(
            model_name='show',
            name='seats_palco4',
        ),
        migrations.RemoveField(
            model_name='show',
            name='seats_platea',
        ),
        migrations.AddField(
            model_name='booking',
            name='seats',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='show',
            name='seat_cols',
            field=models.IntegerField(default=20, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='show',
            name='seat_rows',
            field=models.IntegerField(default=10, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(26)]),
        ),
        migrations.AddField(
            model_name='show',
            name='seats',
            field=models.JSONField(default=dict),
        ),
    ]
