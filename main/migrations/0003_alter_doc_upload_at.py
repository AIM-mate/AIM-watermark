# Generated by Django 3.2.9 on 2021-11-24 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_doc_upload_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doc',
            name='upload_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]