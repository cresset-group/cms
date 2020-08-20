# Generated by Django 2.2.15 on 2020-08-12 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0009_auto_20200406_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='og_description',
            field=models.TextField(blank=True, help_text='Description that will appear on social media posts. It is limited to 300 characters, but it is recommended that you do not use anything over 200.', max_length=300, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='page',
            name='og_title',
            field=models.CharField(blank=True, help_text='Title that will appear on social media posts. This is limited to 100 characters, but Facebook will truncate the title to 88 characters.', max_length=100, verbose_name='title'),
        ),
    ]
