# Generated by Django 5.0.6 on 2024-05-31 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Person', '0004_alter_person_personid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='suggestion',
            old_name='contactDetail',
            new_name='suggestorContactDetail',
        ),
        migrations.RenameField(
            model_name='suggestion',
            old_name='contactOption',
            new_name='suggestorContactOption',
        ),
        migrations.RenameField(
            model_name='suggestion',
            old_name='name',
            new_name='suggestorName',
        ),
        migrations.AddField(
            model_name='suggestion',
            name='photo',
            field=models.ImageField(blank=True, max_length=200, null=True, upload_to='suggestion/person/images'),
        ),
        migrations.AlterField(
            model_name='personrelationship',
            name='relation',
            field=models.CharField(choices=[('Child', 'Child'), ('Spouse', 'Spouse')], default=None, max_length=8),
        ),
    ]
