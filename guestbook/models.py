from django.db import models

# Create your models here.
class Guestbook(models.Model):
    entry_text = models.CharField(max_length=500)
    writer_nickname = models.CharField(max_length=50)
    entry_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.entry_text+" // "+self.writer_nickname+" ("+str(self.entry_datetime)+")"
