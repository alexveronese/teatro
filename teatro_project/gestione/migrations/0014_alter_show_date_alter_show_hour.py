# Generated by Django 5.1 on 2024-09-06 09:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestione', '0013_remove_booking_seats_palco_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='show',
            name='date',
            field=models.DateField(blank=True, default=datetime.date(2024, 9, 6), null=True),
        ),
        migrations.AlterField(
            model_name='show',
            name='hour',
            field=models.TimeField(blank=True, default='21:00', null=True),
        ),
    ]
