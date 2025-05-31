from django.contrib import admin
from crowdsourcing.models import Document,Rectangle, Task, Subtask, Project, UserProject

class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id","name",'description')
admin.site.register(Project, ProjectAdmin)

@admin.action(description="Duplicate documents")
def duplicate(modeladmin, request, queryset):
    for document in queryset:
        original_doc_id = document.id

        document.pk = None
        document.save()
        new_doc_id = document.id

        dico_rectangle={}
        for rectangle in Rectangle.objects.filter(document=Document.objects.get(pk=original_doc_id)):
            original_rect_id = rectangle.id
            rectangle.pk = None
            rectangle.document = document
            rectangle.save()
            dico_rectangle[original_rect_id]=rectangle.id

        dico_task={}
        for task in Task.objects.filter(document=Document.objects.get(pk=original_doc_id)):
            original_task_id = task.id
            task.pk = None
            task.document = document
            task.save()
            dico_task[original_task_id] = task.id


            for subtask in Subtask.objects.filter(task=Task.objects.get(pk=original_task_id)):
                original_subtask_rect = subtask.rectangle.id
                subtask.pk = None
                subtask.task = task
                subtask.rectangle= Rectangle.objects.get(pk=dico_rectangle[original_subtask_rect])
                subtask.save()
    print("duplicate done")

class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id","project",'status',"name", "archive_name")
    actions = [duplicate]
admin.site.register(Document, DocumentAdmin)

class RectangleAdmin(admin.ModelAdmin):
    list_display = ("id","document","done")
admin.site.register(Rectangle, RectangleAdmin)

class TaskAdmin(admin.ModelAdmin):
    list_display = ("id","document","user","status","type")
admin.site.register(Task,TaskAdmin)

class SubtaskAdmin(admin.ModelAdmin):
    list_display = ("id","rectangle","task","text","status")
admin.site.register(Subtask,SubtaskAdmin)

class UserProjectAdmin(admin.ModelAdmin):
    list_display = ("id","project","user","role","participation_amount",'last_participation')
admin.site.register(UserProject,UserProjectAdmin)