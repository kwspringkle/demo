from django.db import models
from django.utils import timezone

class Goal(models.Model):
    goal_name = models.CharField(max_length=255)
    start_day = models.DateField()
    finish_day = models.DateField()
    number_of_task = models.IntegerField()
    ai_response = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.goal_name

class TaskByAI(models.Model):
    task_name = models.CharField(max_length=255)
    start_day = models.DateField(default=timezone.now)
    deadline = models.DateField()
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)

    def __str__(self):
        return self.task_name
