from django.db import models


class Requirement(models.Model):
    """Describe a requirement for anything e.g. schools, scholarships etc.
    This is the parent class of all *Requirement models.
    Attributes:
        name (str): title of requirement (Optional)
        description (str): explanation of requirement (Optional)
    """
    name = models.CharField(max_length=999, blank=True, null=True)
    description = models.CharField(max_length=999, blank=True, null=True)

    @staticmethod
    def get_type():
        return 'Requirement'

    def __str__(self):
        return self.name or '{} #{}'.format(self.get_type(), self.pk or 'N/A')


class School(models.Model):
    name = models.CharField(max_length=250, help_text='Name of Institution')
    type = models.IntegerField(choices=((1, 'university'), (2, 'other')), help_text='Type of institution.')
    location = models.IntegerField(choices=((1, 'Lusaka'), (2, 'Ndola'), (3, 'Choma'), (4, 'Chipata'), (5, 'Kwabe')),
                                   help_text='State location of this school.')
    ownership = models.IntegerField(choices=((1, 'private'), (2, 'public'), ),
                                    help_text='Is it a private school or a public school ?')
    application_info = models.CharField(max_length=9999, help_text="How to apply ?", null=True, blank=True)

    def __str__(self):
        return self.name + " " + self.get_ownership_display() + " university in " + self.get_location_display()


class Faculty(models.Model):
    name = models.CharField(max_length=250, help_text='Name of Faculty')
    description = models.CharField(max_length=500, help_text='Description of Faculty', blank=True, null=True)
    school = models.ForeignKey(School, related_name='faculties')
    application_info = models.CharField(max_length=1250, help_text="How to apply ?", null=True, blank=True)

    def __str__(self):
        return self.name + " at " + self.school.name


class Scholarship(models.Model):
    name = models.CharField(max_length=999, null=True)
    description = models.CharField(max_length=999, blank=True, null=True)
    conditions = models.CharField(max_length=999, help_text='Use Requirements instead. Will be REMOVED.',
                                  null=True, blank=True)
    amount = models.IntegerField(help_text='Amount of money in this scholarship (kwacha).', blank=True, null=True)

    def __str__(self):
        return "{} <amount: {}>".format(self.name or 'Scholarship', self.amount)


class ScholarshipRequirement(Requirement):
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE)

    @staticmethod
    def get_type():
        return 'Scholarship Requirement'


class StudyField(models.Model):
    name = models.CharField(max_length=250,  help_text='Name of this field of study.')
    description = models.CharField(max_length=250, help_text='Description of this field of study.', null=True,
                                   blank=True)

    def __str__(self):
        return self.name


class Career(models.Model):
    name = models.CharField(max_length=250, help_text='Name of this career')
    description = models.CharField(max_length=500, help_text='Description of this career', null=True, blank=True)

    def __str__(self):
        return self.name


class StudyProgram(models.Model):
    name = models.CharField(max_length=250, help_text='Name of this program.')
    description = models.CharField(max_length=2000, blank=True, default='')
    admission_requirements = models.CharField(max_length=9999, blank=True, default='')
    faculty = models.ForeignKey(Faculty, related_name='programs', help_text='Faculty with this program.')
    level = models.IntegerField(choices=((1, 'undergraduate'), (2, 'graduate')), help_text='Level of current program.')
    length = models.IntegerField(help_text='Length of this study program in the selected base unit.')
    base_time_unit = models.IntegerField(choices=((1, 'semester(s)'), (2, 'year(s)')))

    def __str__(self):
        return self.name + " at " + self.faculty.name + " [" + self.get_level_display() + "]"


class FieldCareer(models.Model):
    career = models.ForeignKey(Career, related_name='fields', help_text='Career linked with field of study.')
    field = models.ForeignKey(StudyField, related_name='careers', help_text='Field of study linked with progra2m.')

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
                        help_text='Student category targeted by this tuition (e.g. foreign student, in-state student)')
    period = models.CharField(max_length=25, help_text='Period for tuition payment (e.g. year, semester)')
    payments = models.CharField(max_length=999, help_text='List of payments asked each period. (separator: ";")')
    total = models.IntegerField(help_text='Total amount to pay for tuition for the program.', blank=True, null=True)

    def __str__(self):
        return "Tuition fees for " + self.program.name + ": " + str(self.sum_tuitions()) + " Kwacha"

    def sum_tuitions(self):
        if self.total is None:
            lst_payment = [int(p) for p in self.payments.split(';')]
            self.total = sum(lst_payment)
        return self.total

    def save(self, *args, **kwargs):
        self.total = None
        self.sum_tuitions()
        return super(ProgramTuition, self).save(*args, **kwargs)


class FacultyTuition(models.Model):
    faculty = models.ForeignKey(Faculty, related_name='tuitions', help_text='university faculty linked to this tuition.')
    student_category = models.CharField(max_length=250,
                       help_text='Student category concerned by this tuition (e.g. foreign student, in-state student)')
    period = models.CharField(max_length=25, help_text='Period for tuition payment (e.g. year, semester)')
    payments = models.CharField(max_length=999, help_text='List of payments asked each period. (separator: ";")')
    total = models.IntegerField(blank=True, help_text='Total amount to pay for tuition for the length '
                                                      'of an entire program.', default=0)

    def __str__(self):
        return "Tuition fees for {}: {} Kwacha".format(self.faculty.name, self.sum_tuitions())

    def sum_tuitions(self):
        if self.total is None:
            lst_payment = [int(p) for p in self.payments.split(';')]
            self.total = sum(lst_payment)
        return self.total

    def save(self, *args, **kwargs):
        self.total = None
        self.sum_tuitions()
        return super(FacultyTuition, self).save(*args, **kwargs)
