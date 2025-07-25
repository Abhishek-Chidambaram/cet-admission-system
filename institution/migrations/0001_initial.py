# Generated by Django 4.2.7 on 2025-07-19 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_code', models.CharField(choices=[('CSE', 'Computer Science Engineering'), ('ISE', 'Information Science Engineering'), ('ECE', 'Electronics and Communication Engineering'), ('EEE', 'Electrical and Electronics Engineering'), ('MECH', 'Mechanical Engineering'), ('CIVIL', 'Civil Engineering'), ('BIOTECH', 'Biotechnology'), ('CHEM', 'Chemical Engineering'), ('AERO', 'Aeronautical Engineering'), ('AUTO', 'Automobile Engineering')], max_length=10)),
                ('course_name', models.CharField(max_length=100)),
                ('total_seats', models.IntegerField()),
                ('general_seats', models.IntegerField()),
                ('obc_seats', models.IntegerField()),
                ('sc_seats', models.IntegerField()),
                ('st_seats', models.IntegerField()),
                ('ews_seats', models.IntegerField()),
                ('duration_years', models.IntegerField(default=4)),
                ('fees_per_year', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('code', models.CharField(max_length=10, unique=True)),
                ('institution_type', models.CharField(choices=[('government', 'Government'), ('aided', 'Government Aided'), ('unaided', 'Private Unaided')], max_length=20)),
                ('address', models.TextField()),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(default='Karnataka', max_length=100)),
                ('pincode', models.CharField(max_length=10)),
                ('phone', models.CharField(max_length=17)),
                ('email', models.EmailField(max_length=254)),
                ('website', models.URLField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('established_year', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='SeatMatrix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('available_general', models.IntegerField(default=0)),
                ('available_obc', models.IntegerField(default=0)),
                ('available_sc', models.IntegerField(default=0)),
                ('available_st', models.IntegerField(default=0)),
                ('available_ews', models.IntegerField(default=0)),
                ('cutoff_general', models.IntegerField(blank=True, null=True)),
                ('cutoff_obc', models.IntegerField(blank=True, null=True)),
                ('cutoff_sc', models.IntegerField(blank=True, null=True)),
                ('cutoff_st', models.IntegerField(blank=True, null=True)),
                ('cutoff_ews', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
