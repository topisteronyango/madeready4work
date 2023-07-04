from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField
from django.template.loader import render_to_string



# Create your models here.

class Internship(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    class Meta:
        ordering = ['title']
    def __str__(self):
        return self.title

class Specialization(models.Model):
    project_lead = models.ForeignKey(User,
    related_name='specializations_created',
    on_delete=models.CASCADE)
    internship = models.ForeignKey(Internship,
    related_name='specializations',
    on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(User, related_name='specializations_joined', blank=True)
    class Meta:
        ordering = ['-created']
    def __str__(self):
        return self.title

class Project(models.Model):
    specialization = models.ForeignKey(Specialization,
    related_name='projects',
    on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['specialization'])

    class Meta:
        ordering = ['-order']

    def __str__(self):
        return f'{self.order}. {self.title}'
    


class Content(models.Model):
    project = models.ForeignKey(Project, related_name='contents', on_delete=models.CASCADE)
    # content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # owner = models.ForeignKey(User, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, 
    limit_choices_to={'model__in':('text','video','image','file')}, null=True, default=None)
    order = OrderField(blank=True, for_fields=['project'])
    # order = OrderField(blank=True, for_fields=['specialization'])
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-order']

class ItemBase(models.Model):
    project_lead = models.ForeignKey(User,
    related_name='%(class)s_related',
    on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def render(self):
        return render_to_string(f'projects/content/{self._meta.model_name}.html', {'item': self})
    class Meta:
        abstract = True
    def __str__(self):
        return self.title
class Text(ItemBase):
    content = models.TextField()
class File(ItemBase):
    file = models.FileField(upload_to='files')
class Image(ItemBase):
    file = models.FileField(upload_to='images')
class Video(ItemBase):
    url = models.URLField()
