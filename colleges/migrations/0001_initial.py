# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-07 20:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Career',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('description', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='FieldCareer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('career', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='colleges.Career')),
            ],
        ),
        migrations.CreateModel(
            name='FieldProgram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='ProgramTuition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_category', models.CharField(max_length=250)),
                ('period', models.CharField(max_length=250)),
                ('payments', models.CharField(help_text='List of payments asked each period. (separator: ";")', max_length=999)),
                ('total', models.CharField(help_text='Total amount to pay for tuition for the entire program.', max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Scholarship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conditions', models.CharField(max_length=999)),
                ('amount', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('type', models.IntegerField(choices=[(1, 'university'), (2, 'other')])),
                ('location', models.CharField(choices=[(1, 'Lusaka'), (2, 'Ndola'), (3, 'Choma'), (4, 'Chipata')], max_length=250)),
                ('ownership', models.CharField(choices=[(1, 'private'), (2, 'public')], max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='StudyField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('description', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='StudyProgram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('level', models.IntegerField(choices=[(1, 'undergraduate'), (2, 'graduate')])),
                ('length', models.IntegerField(help_text='Length of this study program in the selected base unit.')),
                ('base_time_unit', models.IntegerField(choices=[(1, 'semester(s)'), (2, 'year(s)')])),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='programs', to='colleges.School')),
            ],
        ),
        migrations.AddField(
            model_name='programtuition',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tuitions', to='colleges.StudyProgram'),
        ),
        migrations.AddField(
            model_name='fieldprogram',
            name='field',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='programs', to='colleges.StudyField'),
        ),
        migrations.AddField(
            model_name='fieldprogram',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='colleges.StudyProgram'),
        ),
        migrations.AddField(
            model_name='fieldcareer',
            name='field',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='careers', to='colleges.StudyField'),
        ),
    ]
