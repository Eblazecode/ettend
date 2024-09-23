# Generated by Django 5.0.7 on 2024-09-22 16:30

import datetime
import django.db.models.deletion
import django.db.models.manager
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_proj', '0003_law_100l_law_200l_law_300l_law_400l_staff_seminar_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='staff_Conference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('staff_name', models.CharField(max_length=50)),
                ('staff_dept', models.CharField(max_length=50)),
                ('conference_title', models.CharField(max_length=50)),
                ('conference_venue', models.CharField(max_length=50)),
                ('conference_date', models.DateField(default=django.utils.timezone.now)),
                ('conference_time', models.TimeField(default=datetime.time(16, 30, 44, 535394))),
                ('conference_type', models.CharField(max_length=50)),
                ('conference_category', models.CharField(max_length=50)),
                ('clock_in', models.TimeField()),
                ('clock_out', models.TimeField()),
                ('remarks', models.CharField(max_length=100)),
                ('attendance_score', models.IntegerField(default=0)),
                ('staff_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attendance_proj.staff')),
            ],
            managers=[
                ('conference', django.db.models.manager.Manager()),
            ],
        ),
    ]
