from django.db import models
from django.urls import reverse

# Default User model
from authentication.models import User
from crowdsourcing.models import Document, Subtask, Rectangle


class Topic(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200, null=True)
    description = models.TextField(max_length=500, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    related_document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True,blank=True)
    related_rectangle = models.ForeignKey(Rectangle, on_delete=models.CASCADE, null=True,blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('topic-detail', kwargs={
            'pk': self.pk
    })

    # Use this method as a property 
    @property
    def answer_count(self):
        return Answer.objects.filter(user_post=self).count()
    
    # Use this method as a property 
    @property
    def topic_view_count(self):
        return TopicView.objects.filter(user_post=self).count()

class TopicView(models.Model):
    user_post = models.ForeignKey(Topic, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)

    def __str__(self):
        return self.user_post.title

class Answer(models.Model):
    user_post = models.ForeignKey(Topic, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    content = models.TextField(max_length=500)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    upvotes = models.ManyToManyField(User, blank=True, related_name='upvotes')
    downvotes = models.ManyToManyField(User, blank=True, related_name='downvotes')

    def __str__(self):
        return self.content
    
    @property
    def upvotes_count(self):
        return Answer.objects.filter(user=self).count()

class Announcement(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.title
