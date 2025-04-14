# Generated by Django 5.1.6 on 2025-02-14 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('login', models.CharField(max_length=255, unique=True)),
                ('age', models.SmallIntegerField()),
                ('location', models.CharField(max_length=255)),
                ('gender', models.CharField(choices=[('MALE', 'Male'), ('FEMALE', 'Female')], max_length=6)),
            ],
        ),
    ]
