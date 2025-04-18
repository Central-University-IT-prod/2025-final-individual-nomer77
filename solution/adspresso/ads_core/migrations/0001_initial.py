# Generated by Django 5.1.6 on 2025-02-19 10:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('advertisers', '0003_remove_campaign_spent_total'),
        ('clients', '0003_client_clicks_count_client_impressions_count'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdEngineSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_ad_cost', models.FloatField(default=-1.0)),
                ('max_ml_score', models.BigIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='ClientClickAd',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.PositiveBigIntegerField()),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_clicks', to='advertisers.campaign')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ad_clicks', to='clients.client')),
            ],
            options={
                'unique_together': {('client', 'campaign')},
            },
        ),
        migrations.CreateModel(
            name='ClientImpressionAd',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.PositiveBigIntegerField()),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_impressions', to='advertisers.campaign')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ad_impressions', to='clients.client')),
            ],
            options={
                'unique_together': {('client', 'campaign')},
            },
        ),
    ]
