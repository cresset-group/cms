# Generated by Django 2.2.9 on 2020-10-09 14:58

from django.db import migrations, models


def fix_country_default(apps, schema_editor):
    '''Changes any countries with a default of False to unset. False is no longer a selectable option in the admin'''
    Country = apps.get_model('pages', 'Country')
    Country.objects.filter(default=False).update(default=None)


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0011_auto_20200916_1614'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ['name'], 'verbose_name_plural': 'countries'},
        ),
        migrations.RunPython(
            fix_country_default,
        ),
        migrations.AlterField(
            model_name='country',
            name='default',
            field=models.BooleanField(blank=True, choices=[(True, 'Yes'), (None, 'No')], default=None, null=True, unique=True),
        ),
    ]
