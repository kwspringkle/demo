from django.db import models
from goal.models import Goal

def get_comic_image_path(instance, filename):
    # This will save images to 'media/comics/<comic_id>/<filename>'
    return f'comics/{instance.comic.id}/{filename}'

class Comic(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    goal=models.ForeignKey(Goal, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

class Panel(models.Model):
    comic = models.ForeignKey(Comic, on_delete=models.CASCADE, related_name='panels')
    image = models.ImageField(upload_to=get_comic_image_path)
    panel_number = models.IntegerField()

    def __str__(self):
        return f"Panel {self.panel_number} of {self.comic.title}"
