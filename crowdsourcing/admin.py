from django.contrib import admin
from crowdsourcing.models import Document,Rectangle, Task, Subtask, Project, UserProject

class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id","name",'description')
admin.site.register(Project, ProjectAdmin)

class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id","project",'status',"name")
admin.site.register(Document, DocumentAdmin)

class RectangleAdmin(admin.ModelAdmin):
    list_display = ("id","document","done")
admin.site.register(Rectangle, RectangleAdmin)


class TaskAdmin(admin.ModelAdmin):
    list_display = ("document","user","status","type")
admin.site.register(Task,TaskAdmin)

class SubtaskAdmin(admin.ModelAdmin):
    list_display = ("rectangle","task","text","status")
admin.site.register(Subtask,SubtaskAdmin)

class UserProjectAdmin(admin.ModelAdmin):
    list_display = ("project","user","role","participation_amount",'last_participation')
admin.site.register(UserProject,UserProjectAdmin)
