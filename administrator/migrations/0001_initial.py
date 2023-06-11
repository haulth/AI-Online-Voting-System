# Generated by Django 4.1.7 on 2023-06-10 13:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userid', models.CharField(max_length=10)),
                ('date', models.DateField(auto_now_add=True)),
                ('time_in', models.TimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emcode', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=50)),
                ('department', models.CharField(max_length=50)),
                ('gender', models.CharField(max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
