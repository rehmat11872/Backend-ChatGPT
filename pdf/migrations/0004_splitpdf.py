# Generated by Django 4.2.7 on 2024-01-23 21:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pdf', '0003_compressedpdf'),
    ]

    operations = [
        migrations.CreateModel(
            name='SplitPDF',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_page', models.IntegerField()),
                ('end_page', models.IntegerField()),
                ('split_pdf', models.FileField(upload_to='split_pdfs/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
