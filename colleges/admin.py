from django.contrib import admin

# Register your models here.
from .models import School, Scholarship, StudyField, Career, StudyProgram, FieldCareer, FieldProgram, ProgramTuition


admin.site.register(School)
admin.site.register(Scholarship)
admin.site.register(StudyField)
admin.site.register(Career)
admin.site.register(StudyProgram)
admin.site.register(FieldCareer)
admin.site.register(FieldProgram)
admin.site.register(ProgramTuition)
