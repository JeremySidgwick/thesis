from django.contrib import admin
from .models import *


class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("id","title",'slug')

admin.site.register(BlogPost, BlogPostAdmin)



admin.site.register(Answer)
admin.site.register(TopicView)



class UserPostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", 'title','related_document','related_rectangle')
admin.site.register(UserPost, UserPostAdmin)