# Generated by Django 5.0.6 on 2024-06-02 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Person', '0006_alter_personrelationship_relation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='personrelationship',
            name='relation',
            field=models.CharField(choices=[('Child', 'Child'), ('Spouse', 'Spouse')], default=None, max_length=8),
        ),
    ]