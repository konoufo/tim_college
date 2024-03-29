from django.contrib import admin

from colleges import models


class ScholarshipRequirementAdminInline(admin.StackedInline):
    model = models.ScholarshipRequirement


class ScholarshipAdmin(admin.ModelAdmin):
    inlines = [
        ScholarshipRequirementAdminInline
    ]

    
class FieldCareerAdmin(admin.ModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):
        # here we define a custom template
        self.change_form_template = 'admin/tim/change_form_help_text.html'
        extra = {
            'help_text': """This represents every linked career and field of study.
                            In the sense that many fields can lead to the same career.
                            Whereas many careers can span from one field of study."""
        }

        context.update(extra)
        return super(FieldCareerAdmin, self).render_change_form(request, context, *args, **kwargs)


class FieldProgramAdmin(admin.ModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):
        # here we define a custom template
        self.change_form_template = 'admin/tim/change_form_help_text.html'
        extra = {
            'help_text': """This represents every linked school program and field of study.
                            In the sense that there are many programs in a same field of study.
                            Whereas a program could span several fields of study."""
        }

        context.update(extra)
        return super(FieldProgramAdmin, self).render_change_form(request, context, *args, **kwargs)


class StudyProgramAdmin(admin.ModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):
        # here we define a custom template
        self.change_form_template = 'admin/tim/change_form_help_text.html'
        extra = {
            'help_text': """This represents an official university program.

                            """
        }

        context.update(extra)
        return super(StudyProgramAdmin, self).render_change_form(request, context, *args, **kwargs)


class StudyFieldAdmin(admin.ModelAdmin):
    def render_change_form(self, request, context, *args, **kwargs):
        # here we define a custom template
        self.change_form_template = 'admin/tim/change_form_help_text.html'
        extra = {
            'help_text': """This represents an arbitrary field of study i.e Mathematics, Sociology, or Robotics.
                            It is NOT an official university program per se, it's the larger area of knowledge
                            a university program can be taken from. Ex: BSc in Mathematics and CS is part of
                            the study fields of Mathematics and also of Computing.
                             """
        }

        context.update(extra)
        return super(StudyFieldAdmin, self).render_change_form(request, context, *args, **kwargs)


class FacultyTuitionAdmin(admin.ModelAdmin):
    fields = ('faculty', 'student_category', 'payments', 'period')


class ProgramTuitionAdmin(admin.ModelAdmin):
    fields = ('program', 'student_category', 'payments', 'period')


admin.site.register(models.School)
admin.site.register(models.Scholarship, ScholarshipAdmin)
admin.site.register(models.StudyField, StudyFieldAdmin)
admin.site.register(models.Career)
admin.site.register(models.StudyProgram, StudyProgramAdmin)
admin.site.register(models.FieldCareer, FieldCareerAdmin)
admin.site.register(models.FieldProgram, FieldProgramAdmin)
admin.site.register(models.ProgramTuition, ProgramTuitionAdmin)
admin.site.register(models.Faculty)
admin.site.register(models.FacultyTuition, FacultyTuitionAdmin)
