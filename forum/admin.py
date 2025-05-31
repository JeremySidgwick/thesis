from django.contrib import admin
from .models import *


class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("id","title")

admin.site.register(Announcement, BlogPostAdmin)


class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id","user_post",'user','content')
admin.site.register(Answer,AnswerAdmin)



admin.site.register(TopicView)


class UserPostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", 'title','related_document','related_rectangle')
admin.site.register(Topic, UserPostAdmin)