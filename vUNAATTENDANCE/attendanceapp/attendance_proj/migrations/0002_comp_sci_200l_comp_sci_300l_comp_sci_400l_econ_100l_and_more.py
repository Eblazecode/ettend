# Generated by Django 5.0.7 on 2024-08-13 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance_proj', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comp_sci_200l',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matric_num', models.CharField(max_length=20, unique=True)),
                ('student_name', models.CharField(max_length=50)),
                ('CSC_201', models.IntegerField(default=0)),
                ('CSC_202', models.IntegerField(default=0)),
                ('CSC_203', models.IntegerField(default=0)),
                ('CSC_204', models.IntegerField(default=0)),
                ('level', models.IntegerField(default=200)),
                ('week', models.IntegerField(default=1)),
                ('total_attendance_score', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Comp_sci_300l',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matric_num', models.CharField(max_length=20, unique=True)),
                ('student_name', models.CharField(max_length=50)),
                ('CSC_301', models.IntegerField(default=0)),
                ('CSC_302', models.IntegerField(default=0)),
                ('CSC_303', models.IntegerField(default=0)),
                ('CSC_304', models.IntegerField(default=0)),
                ('level', models.IntegerField(default=300)),
                ('week', models.IntegerField(default=1)),
                ('total_attendance_score', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Comp_sci_400l',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matric_num', models.CharField(max_length=20, unique=True)),
                ('student_name', models.CharField(max_length=50)),
                ('CSC_401', models.IntegerField(default=0)),
                ('CSC_402', models.IntegerField(default=0)),
                ('CSC_403', models.IntegerField(default=0)),
                ('CSC_404', models.IntegerField(default=0)),
                ('level', models.IntegerField(default=400)),
                ('week', models.IntegerField(default=1)),
                ('total_attendance_score', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Econ_100l',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matric_num', models.CharField(max_length=20, unique=True)),
                ('student_name', models.CharField(max_length=50)),
                ('ECO_101', models.IntegerField(default=0)),
                ('ECO_102', models.IntegerField(default=0)),
                ('ECO_103', models.IntegerField(default=0)),
                ('ECO_104', models.IntegerField(default=0)),
                ('level', models.IntegerField(default=100)),
                ('week', models.IntegerField(default=1)),
                ('total_attendance_score', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Econ_200l',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matric_num', models.CharField(max_length=20, unique=True)),
                ('student_name', models.CharField(max_length=50)),
                ('ECO_201', models.IntegerField(default=0)),
                ('ECO_202', models.IntegerField(default=0)),
                ('ECO_203', models.IntegerField(default=0)),
                ('ECO_204', models.IntegerField(default=0)),
                ('level', models.IntegerField(default=200)),
                ('week', models.IntegerField(default=1)),
                ('total_attendance_score', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Econ_300l',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matric_num', models.CharField(max_length=20, unique=True)),
                ('student_name', models.CharField(max_length=50)),
                ('ECO_301', models.IntegerField(default=0)),
                ('ECO_302', models.IntegerField(default=0)),
                ('ECO_303', models.IntegerField(default=0)),
                ('ECO_304', models.IntegerField(default=0)),
                ('level', models.IntegerField(default=300)),
                ('week', models.IntegerField(default=1)),
                ('total_attendance_score', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Econ_400l',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matric_num', models.CharField(max_length=20, unique=True)),
                ('student_name', models.CharField(max_length=50)),
                ('ECO_401', models.IntegerField(default=0)),
                ('ECO_402', models.IntegerField(default=0)),
                ('ECO_403', models.IntegerField(default=0)),
                ('ECO_404', models.IntegerField(default=0)),
                ('level', models.IntegerField(default=400)),
                ('week', models.IntegerField(default=1)),
                ('total_attendance_score', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Pol_sci_100l',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matric_num', models.CharField(max_length=20, unique=True)),
                ('student_name', models.CharField(max_length=50)),
                ('POL_101', models.IntegerField(default=0)),
                ('POL_102', models.IntegerField(default=0)),
                ('POL_103', models.IntegerField(default=0)),
                ('POL_104', models.IntegerField(default=0)),
                ('level', models.IntegerField(default=100)),
                ('week', models.IntegerField(default=1)),
                ('total_attendance_score', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Pol_sci_200l',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matric_num', models.CharField(max_length=20, unique=True)),
                ('student_name', models.CharField(max_length=50)),
                ('POL_201', models.IntegerField(default=0)),
                ('POL_202', models.IntegerField(default=0)),
                ('POL_203', models.IntegerField(default=0)),
                ('POL_204', models.IntegerField(default=0)),
                ('level', models.IntegerField(default=200)),
                ('week', models.IntegerField(default=1)),
                ('total_attendance_score', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Pol_sci_300l',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matric_num', models.CharField(max_length=20, unique=True)),
                ('student_name', models.CharField(max_length=50)),
                ('POL_301', models.IntegerField(default=0)),
                ('POL_302', models.IntegerField(default=0)),
                ('POL_303', models.IntegerField(default=0)),
                ('POL_304', models.IntegerField(default=0)),
                ('level', models.IntegerField(default=300)),
                ('week', models.IntegerField(default=1)),
                ('total_attendance_score', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Pol_sci_400l',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matric_num', models.CharField(max_length=20, unique=True)),
                ('student_name', models.CharField(max_length=50)),
                ('POL_401', models.IntegerField(default=0)),
                ('POL_402', models.IntegerField(default=0)),
                ('POL_403', models.IntegerField(default=0)),
                ('POL_404', models.IntegerField(default=0)),
                ('level', models.IntegerField(default=400)),
                ('week', models.IntegerField(default=1)),
                ('total_attendance_score', models.IntegerField(default=0)),
            ],
        ),
    ]
