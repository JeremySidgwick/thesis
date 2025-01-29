from django.contrib import admin
from authentication.models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ("id","username","completed_tasks")
admin.site.register(User,UserAdmin)