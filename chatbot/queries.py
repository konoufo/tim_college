# Query functions
from colleges import models


def get_all_schools():
    return models.School.objects.all()


def find_schools_by_region(region):
    return models.School.objects.filter(location=region)


def find_school_by_name(name):
    return models.School.objects.get(name=name)


def find_study_programs_by_faculty(faculty):
    return models.StudyProgram.objects.filter(faculty=faculty)


def find_program_tuition_by_study_program(program):
    return models.ProgramTuition.objects.get(program=program)


def find_study_programs_by_study_field(study_field):
    return models.FieldProgram.objects.filter(field=study_field)


def get_all_faculties():
    return models.Faculty.objects.all()


def find_faculties_by_school(school):
    return models.Faculty.objects.filter(school=school)


def find_faculty_by_name(name):
    return models.Faculty.objects.get(name=name)

# TODO: Add scholarship field in program model


def is_scholarship_available():
    return


# def find_scholarship_by_program_name(program_name):
#    return models.Scholarship.objects.get(program.name=program_name)


def get_all_study_fields():
    return models.StudyField.objects.all()


def find_study_field_by_name(name):
    return models.StudyField.objects.get(name=name)


def get_all_careers():
    return models.Career.objects.all()


def find_career_by_name(name):
    return models.Career.objects.get(name=name)


def find_career_by_study_field(study_field):
    return models.FieldCareer.objects.filter(field=study_field)

