from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('inbox/<str:inbox_file>', views.inbox, name="inbox"),
    path('archive/', views.archive, name="archive"),
    path('archive/<int:id>', views.edit, name="edit"),
    path('download/<filefolder>/<filename>', views.download, name='download'),
]
