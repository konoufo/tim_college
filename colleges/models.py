from django.db import models


class School(models.Model):
    name = models.CharField(max_length=250, help_text='Name of Institution')
    type = models.IntegerField(choices=((1, 'university'), (2, 'other')), help_text='Type of institution.')
    location = models.IntegerField(choices=((1, 'Lusaka'), (2, 'Ndola'), (3, 'Choma'), (4, 'Chipata'), ),
                                   help_text='State location of this school.')
    ownership = models.IntegerField(choices=((1, 'private'), (2, 'public'), ),
                                    help_text='Is it a private school or a public school ?')

    def __str__(self):
        return self.name + " " + self.get_ownership_display() + " university in " + self.get_location_display()


class Faculty(models.Model):
    name = models.CharField(max_length=250, help_text='Name of Faculty')
    description = models.CharField(max_length=500, help_text='Description of Faculty')
    school = models.ForeignKey(School, related_name='faculties')
    application_info = models.CharField(max_length=1250)

    def __str__(self):
        return self.name + " at " + self.school.name


class Scholarship(models.Model):
    conditions = models.CharField(max_length=999, help_text='List of conditions for this scholarship. (separator: ";")')
    amount = models.IntegerField(help_text='Amount of money in this scholarship.')

    def __str__(self):
        return "Amount available: " + str(self.amount)


class StudyField(models.Model):
    name = models.CharField(max_length=250,  help_text='Name of this field of study.')
    description = models.CharField(max_length=250, help_text='Description of this field of study.')

    def __str__(self):
        return self.name


class Career(models.Model):
    name = models.CharField(max_length=250, help_text='Name of this career')
    description = models.CharField(max_length=500, help_text='Description of this career')

    def __str__(self):
        return self.name


class StudyProgram(models.Model):
    name = models.CharField(max_length=250, help_text='Name of this program.')
    description = models.CharField(max_length=500, blank=True, default='')
    faculty = models.ForeignKey(Faculty, related_name='programs', help_text='Faculty with this program.')
    level = models.IntegerField(choices=((1, 'undergraduate'), (2, 'graduate')),
                                help_text='Level of current program.')
    length = models.IntegerField(help_text='Length of this study program in the selected base unit.')
    base_time_unit = models.IntegerField(choices=((1, 'semester(s)'), (2, 'year(s)')))

    def __str__(self):
        return self.name + " at " + self.faculty.name + " [" + self.get_level_display() + "]"


class FieldCareer(models.Model):
    career = models.ForeignKey(Career, related_name='fields', help_text='Career linked with field of study.')
    field = models.ForeignKey(StudyField, related_name='careers', help_text='Field of study linked with program.')

    def __str__(self):
        return self.career.name


class FieldProgram(models.Model):
    program = models.ForeignKey(StudyProgram, related_name='fields', help_text='Program linked with field of study.')
    field = models.ForeignKey(StudyField, related_name='programs', help_text='Field of study linked with program.')

    def __str__(self):
        return self.program.name


class ProgramTuition(models.Model):
    program = models.ForeignKey(StudyProgram, related_name='tuitions',
                                help_text='university program linked to this tuition.')
    student_category = models.CharField(max_length=250,
                        help_text='Student category concerned by this tuition (e.g. foreign student, in-state student)')
    period = models.CharField(max_length=25, help_text='Period for tuition payment (e.g. year, semester)')
    payments = models.CharField(max_length=999, help_text='List of payments asked each period. (separator: ";")')
    total = models.IntegerField(help_text='Total amount to pay for tuition for the entire program.')

    def __str__(self):
        return "Tuition fees for " + self.program.name + ": " + str(self.sum_tuitions())

    def sum_tuitions(self):
        total = 0
        lst_payment = self.payments.split(';')
        for payment in lst_payment:
            total += int(payment)
        self.total = total
        return total


class FacultyTuition(models.Model):
    faculty = models.ForeignKey(Faculty, related_name='tuitions',
                                help_text='university faculty linked to this tuition.')
    student_category = models.CharField(max_length=250,
                        help_text='Student category concerned by this tuition (e.g. foreign student, in-state student)')
    period = models.CharField(max_length=25, help_text='Period for tuition payment (e.g. year, semester)')
    payments = models.CharField(max_length=999, help_text='List of payments asked each period. (separator: ";")')
    total = models.IntegerField(blank=True, help_text='Total amount to pay for tuition for the length of an entire program.',
                                default=0)

    def __str__(self):
        return "Tuition fees for " + self.faculty.name + ": " + str(self.sum_tuitions())

    def sum_tuitions(self):
        total = 0
        lst_payment = self.payments.split(';')
        for payment in lst_payment:
            total += int(payment)
        self.total = total
        return total
