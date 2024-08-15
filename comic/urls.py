from django.urls import path
from .views import generate_comic_view, view_comic

urlpatterns = [
    path('generate-comic/', generate_comic_view, name='generate_comic'),
    path('view-comic/<int:comic_id>/', view_comic, name='view_comic'),
]