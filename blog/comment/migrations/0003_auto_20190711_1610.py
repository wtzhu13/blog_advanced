# Generated by Django 2.2.3 on 2019-07-11 16:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comment', '0002_auto_20190711_1608'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='comment',
            new_name='content',
        ),
        migrations.RenameField(
            model_name='message',
            old_name='parent_comment',
            new_name='parent_message',
        ),
        migrations.RenameField(
            model_name='message',
            old_name='publisher_id',
            new_name='publisher',
        ),
    ]