# Generated by Django 3.1.5 on 2021-01-21 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('papermanager', '0002_remove_paper_file_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupstorage',
            name='group_max_storage',
            field=models.IntegerField(default=0, verbose_name='Group Storage (MB)'),
        ),
        migrations.AlterField(
            model_name='groupstorage',
            name='user_init_storage',
            field=models.IntegerField(default=0, verbose_name='Default User Storage (MB)'),
        ),
        migrations.AlterField(
            model_name='userstorage',
            name='specific_storage',
            field=models.IntegerField(default=0, verbose_name='Purchased Storage (MB)'),
        ),
    ]
