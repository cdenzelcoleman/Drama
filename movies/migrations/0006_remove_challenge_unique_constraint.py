# Generated by Django 5.2 on 2025-06-02 22:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0005_remove_rooms'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='challenge',
            unique_together=set(),
        ),
    ]
