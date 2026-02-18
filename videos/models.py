from django.db import models

class Video(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # For simplicity, we'll use a URL field or FileField. Let's use FileField for uploads, 
    # but for this demo I'll also add a thumbnail field.
    # In a real app, you might want to use a cloud storage or a dedicated video hosting service.
    video_file = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    duration = models.DurationField(help_text="Duration of the video")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
