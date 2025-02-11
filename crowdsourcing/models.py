from django.db import models
# from ckeditor.fields import RichTextField
from authentication.models import User


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Document(models.Model):
    STATUS_CHOICES = (
        ("to_transcribe", "To Transcribe"),
        ("in_transcription", "In Transcription"),
        ("to_verify", "To Verify"),
        ("in_verification", "In Verification"),
        ("completed", "Completed"),
    )
    image = models.ImageField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="documents")
    status = models.CharField(default="to_transcribe", choices=STATUS_CHOICES, max_length=100)
    name = models.CharField(default="", max_length=200,null=True,blank=True)
    # metadata = models.TextField()


class Rectangle(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="rectangles")
    x = models.IntegerField()
    y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    angle = models.FloatField(default=0)
    done = models.BooleanField(default=False)


class Task(models.Model):
    STATUS_CHOICES = (
        ("in_progress", "In progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("timeout", "Timeout")
    )

    TYPE_CHOICES = (
        ("transcription", "Transcription"),
        ("verification", "Verification")
    )
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="tasks")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    stated = models.DateTimeField(auto_now_add=True)
    ended = models.DateTimeField()
    status = models.CharField(default="in_progress", choices=STATUS_CHOICES, max_length=100) # in progress / aborted / timeout / done
    type = models.CharField(default="transcription", choices=TYPE_CHOICES, max_length=100) #transcription / verification


class Subtask(models.Model):

    STATUS_CHOICES=(
        ("in_progress", "In progress"),
        ("completed", "Completed"),
    )

    rectangle = models.ForeignKey(Rectangle, on_delete=models.CASCADE, related_name="subtasks")
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="subtasks")
    text = models.TextField() #TODO en rich field
    time = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(default='')
    status = models.CharField(default="in_progress", choices=STATUS_CHOICES ,max_length=100) #in_progress ou done



class UserProject(models.Model):

    ROLE_CHOICES = (
        ("manager", "Manager"),
        ("verifier", "Verifier"),
        ("transcriber", "Transcriber"),
        {"candidate","Candidate"},
        {'block','Block'}
    )

    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="user")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="project")
    role = models.CharField(max_length=100,choices=ROLE_CHOICES,default="Transcriber")
    last_participation = models.DateTimeField() #TODO à voir les dates en django
    participation_amount = models.IntegerField(default=0)
