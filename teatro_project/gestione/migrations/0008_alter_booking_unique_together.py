# Generated by Django 5.1 on 2024-09-03 13:04

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestione', '0007_remove_seat_show_remove_booking_seats_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='booking',
            unique_together={('show', 'user')},
        ),
    ]
