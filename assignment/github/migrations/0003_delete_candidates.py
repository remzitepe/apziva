# Generated by Django 4.0.3 on 2022-04-11 12:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('github', '0002_candidates_delete_snippet'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Candidates',
        ),
    ]
