from django.db import models


class School(models.Model):
    name = models.CharField(max_length=250)
    type = models.IntegerField(choices=((1, 'university'), (2, 'other')))
    location = models.IntegerField(choices=((1, 'Lusaka'), (2, 'Ndola'), (3, 'Choma'), (4, 'Chipata'), ))
    ownership = models.IntegerField(choices=((1, 'private'), (2, 'public'), ))

    def __str__(self):
        return self.name + " " + self.get_ownership_display() + " university in " + self.get_location_display()


class Scholarship(models.Model):
    conditions = models.CharField(max_length=999)
    amount = models.IntegerField()

    def __str__(self):
        return "Amount available: " + str(self.amount)


class StudyField(models.Model):
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class Career(models.Model):
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=500)

    def __str__(self):
        return self.name


class StudyProgram(models.Model):
    name = models.CharField(max_length=250)
    school = models.ForeignKey(School, related_name='programs')
    level = models.IntegerField(choices=((1, 'undergraduate'), (2, 'graduate')))
    length = models.IntegerField(help_text='Length of this study program in the selected base unit.')
    base_time_unit = models.IntegerField(choices=((1, 'semester(s)'), (2, 'year(s)')))

    def __str__(self):
        return self.name + " at " + self.school.name + " [" + self.get_level_display() + "]"


class FieldCareer(models.Model):
    career = models.ForeignKey(Career, related_name='fields')
    field = models.ForeignKey(StudyField, related_name='careers')

    def __str__(self):
        return self.career.name


class FieldProgram(models.Model):
    program = models.ForeignKey(StudyProgram, related_name='fields')
    field = models.ForeignKey(StudyField, related_name='programs')

    def __str__(self):
        return self.program.name


class ProgramTuition(models.Model):
    program = models.ForeignKey(StudyProgram, related_name='tuitions')
    student_category = models.CharField(max_length=250)
    period = models.CharField(max_length=25)
    payments = models.CharField(max_length=999, help_text='List of payments asked each period. (separator: ";")')
    total = models.IntegerField(help_text='Total amount to pay for tuition for the entire program.')

    def __str__(self):
        return "Tuition fees for " + self.program.name + ": " + str(self.total)
