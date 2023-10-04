from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('scaninput/', views.scaninput, name="scaninput"),
    path('inbox/', views.inbox, name="inbox"),
    path('archive/', views.archive, name="archive"),
    path('archive/<int:id>', views.edit, name="edit"),
    path('tags/', views.tags, name="tags"),
    path('doctypes/', views.doctypes, name="doctypes"),
    path('download/<filefolder>/<filename>', views.download, name='download'),
    path('download_inbox/<file>', views.download_inbox, name='download_inbox'),
]
