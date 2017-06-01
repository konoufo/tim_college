# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-05-31 22:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colleges', '0001_initial'),
    ]

    operations = [
        migrations.AlterField('StudyProgram', 'description', models.CharField(max_length=2000, blank=True, default='')),
        migrations.RunSQL(
            '''CREATE INDEX program_description_tsv_idx ON colleges_studyprogram 
               USING gin(to_tsvector(\'english\', coalesce(description,'') || ' ' || coalesce(name,'')))'''
        )
    ]
