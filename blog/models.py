from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.utils.text import slugify


class User(AbstractUser):
    def __str__(self):
        return self.username


class Tag(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200, validators=[MinLengthValidator(5)])
    content = models.TextField(validators=[MinLengthValidator(10)])
    content_preview = models.CharField(max_length=300, editable=False)
    slug = models.SlugField(unique=True, db_index=True)
    date = models.DateTimeField(auto_now_add=True, editable=False)
    tags = models.ManyToManyField(Tag, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if len(self.content) > 297:
            self.content_preview = self.content[:297] + '...'
        else:
            self.content_preview = self.content
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
