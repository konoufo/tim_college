from django.db import models


class School(models.Model):
    name = models.CharField(max_length=250)
    type = models.IntegerField(choices=((1, 'university'), (2, 'other')))
    location = models.CharField(max_length=250, choices=((1, 'Lusaka'), (2, 'Ndola'), (3, 'Choma'), (4, 'Chipata'), ))
    ownership = models.CharField(max_length=250, choices=((1, 'private'), (2, 'public'), ))


class Scholarship(models.Model):
    conditions = models.CharField(max_length=999)
    amount = models.IntegerField()


class StudyField(models.Model):
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=250)


class Career(models.Model):
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=500)


class StudyProgram(models.Model):
    name = models.CharField(max_length=250)
    school = models.ForeignKey(School, related_name='programs')
    level = models.IntegerField(choices=((1, 'undergraduate'), (2, 'graduate')))
    length = models.IntegerField(help_text='Length of this study program in the selected base unit.')
    base_time_unit = models.IntegerField(choices=((1, 'semester(s)'), (2, 'year(s)')))


class FieldCareer(models.Model):
    career = models.ForeignKey(Career, related_name='fields')
    field = models.ForeignKey(StudyField, related_name='careers')


class FieldProgram(models.Model):
    program = models.ForeignKey(StudyProgram, related_name='fields')
    field = models.ForeignKey(StudyField, related_name='programs')


class ProgramTuition(models.Model):
    program = models.ForeignKey(StudyProgram, related_name='tuitions')
    student_category = models.CharField(max_length=250)
    period = models.CharField(max_length=250)
    payments = models.CharField(max_length=999, help_text='List of payments asked each period. (separator: ";")')
    total = models.CharField(max_length=250, help_text='Total amount to pay for tuition for the entire program.')
