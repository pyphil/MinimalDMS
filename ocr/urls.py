from django.urls import path
from . import views

urlpatterns = [
    path('', views.archive, name="archive"),
    path('archive/<int:id>', views.edit, name="edit"),
    path('inbox/', views.inbox, name="inbox"),
    path('scaninput/', views.scaninput, name="scaninput"),
    path('inbox_scaninput/', views.inbox_scaninput, name="inbox_scaninput"),
    path('tags/', views.tags, name="tags"),
    path('doctypes/', views.doctypes, name="doctypes"),
    path('persons/', views.persons, name="persons"),
    path('download/<filefolder>/<filename>', views.download, name='download'),
    path('download_inbox/<file>', views.download_inbox, name='download_inbox'),
]
