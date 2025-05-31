from django.urls import path

from .import views

urlpatterns = [
    path('forum/', views.home, name='forum'),
    path('user-post/<str:type>/<int:id>', views.userPost, name='user-post'),
    path('topic/<int:id>/', views.postTopic, name='topic-detail'),
    path('search-result/', views.searchView, name='search-result'),
    path('user-dashboard/', views.userDashboard, name='user-dashboard'),
    path('upvote/', views.upvote, name='upvote'),
    path('downvote/', views.downvote, name='downvote'),
    path('announcements/', views.announcementsList, name='announcements'),
    path('announcements/<int:id>/', views.announcementView, name='announcement-detail'),
]
