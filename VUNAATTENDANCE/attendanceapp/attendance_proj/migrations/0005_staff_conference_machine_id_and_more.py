# Generated by Django 5.0.7 on 2024-09-22 17:24

import datetime
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_proj', '0004_staff_conference'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff_conference',
            name='machine_id',
            field=models.CharField(default=django.utils.timezone.now, max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='staff_conference',
            name='conference_time',
            field=models.TimeField(default=datetime.time(17, 23, 32, 330076)),
        ),
    ]
