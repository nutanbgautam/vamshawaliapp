# Generated by Django 5.0.6 on 2024-05-26 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Person', '0002_alter_person_address_alter_person_aliveordead_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='address',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='person',
            name='cityOrCountry',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='person',
            name='contactDetails',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='person',
            name='emailAddress',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]