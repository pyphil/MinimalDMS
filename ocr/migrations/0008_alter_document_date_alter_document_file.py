# Generated by Django 4.0.6 on 2022-07-22 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ocr', '0007_alter_document_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='file',
            field=models.FileField(upload_to='data/60986d9d-e972-4fc8-8c22-ecd54313b1e6'),
        ),
    ]
