# Generated by Django 5.0.6 on 2024-05-26 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Person', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='address',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='person',
            name='aliveOrDead',
            field=models.CharField(blank=True, default='Unkown', max_length=7),
        ),
        migrations.AlterField(
            model_name='person',
            name='birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='bookReferenceNumber',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='person',
            name='cityOrCountry',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='person',
            name='contactDetails',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='person',
            name='emailAddress',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
