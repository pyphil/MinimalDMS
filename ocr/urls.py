from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('archive/', views.archive, name="archive"),
    path('archive/<int:id>', views.edit, name="edit"),
    path('download/<filefolder>/<filename>', views.download, name='download'),
]
