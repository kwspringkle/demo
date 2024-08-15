from django.db import models
from goal.models import Goal

# Create your models here.
class Events(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)  
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, null=True, blank=True)

    
    class Meta:
        db_table = "tblevents"

    def __str__(self):
        return self.name
