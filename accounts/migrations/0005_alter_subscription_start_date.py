# Generated by Django 4.2.6 on 2023-11-13 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_subscriptionplan_subscription_user_subscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Start Date'),
        ),
    ]
