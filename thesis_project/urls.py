"""
URL configuration for thesis_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from crowdsourcing import views
from authentication import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),

    path('transcription/<int:doc_id>/', views.TranscriptionPage.as_view(), name='transcription_page'),
    path('',views.main_page,name="main_page"),
    path('project/<int:project_id>/', views.project_page, name='project_page'),
    path('verification/<int:doc_id>/', views.VerificationPage.as_view(), name='verification_page'),
    path('completed/<int:doc_id>/',views.completed_page, name='completed_page'),


    # others
    path('save_rectangles/', views.save_rectangles, name='save_rectangles'),
    path('login/', auth_views.login_page, name='login'),
    path('help/', views.help, name='help'),
    path('about/', views.about, name='about'),
    path('logout/', auth_views.logout_user, name='logout'),
    path('signup/', auth_views.signup_page, name='signup'),
    path('', include('forum.urls')),

    path('export/<str:type>/<str:export>/<int:id>',views.export_data,name='export_data'),

    path("preview/<int:doc_id>",views.preview_page,name='preview_page'),
    path("upload/",views.FileFieldFormView.as_view(),name='upload'),

]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

