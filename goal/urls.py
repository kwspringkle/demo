from django.urls import path
from . import views

urlpatterns = [
    path('goals/', views.list_goals, name='list_goals'),
    path('goals/new/', views.create_goal, name='create_goal'),
    path('goals/<int:goal_id>/', views.view_AI_suggestion, name='view_ai_suggestion'),
    path('goals/<int:goal_id>/edit/', views.update_goals, name='update_goals'),
    path('goals/<int:goal_id>/delete/', views.delete_goals, name='delete_goals'),
]
