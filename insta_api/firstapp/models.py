from django.db import models
from django.urls import reverse
# from django.contrib.auth.models import User #this is the User that we find at the /admin page
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect

User = get_user_model()


# Create your models here.
class UserProfileInfo(models.Model):
    # Create relationtship (don't inherit from User!)
    user = models.OneToOneField(User, on_delete=models.PROTECT)  # This is like an extension of the User class

    # Add any additional attributes you want
    portfolio_site = models.URLField(blank=True)  # It is not required
    # pip install pillow to use this!

    # The profile_pics has to be an fodler inside of the media directory we added last time
    profile_pic = models.ImageField(upload_to='profile_pics')
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=20)
    school = models.CharField(max_length=20, blank=True)
    college = models.CharField(max_length=20, blank=True)
    sex = models.CharField(max_length=10)

    def __str__(self):
        return self.user.username


class Friends(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.PROTECT)
    user2 = models.ForeignKey(User, on_delete=models.PROTECT, related_name='user2')
    friend_status = models.PositiveIntegerField(null=False, default=0)

    def __str__(self):
        return self.user1.username


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # title=models.CharField(max_length=200)
    text = models.TextField(max_length=300)
    created_date = models.DateTimeField(default=timezone.now)
    post_pics = models.ImageField(upload_to='post_pics', blank=True)

    # published_date=models.DateTimeField(blank=True,null=True)

    #    def publish(self):
    #        self.published_date=timezone.now()
    #        self.save()

    def approve_comments(self):
        return self.comments.filter(approved_comment=True)

    def get_absolute_url(self):
        return reverse("firstapp:post_detail", kwargs={'pk': self.pk})

    #        return reverse("firstapp:post_list")
    def __str__(self):
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=100,null=False,blank=False)
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self.approved_comment = True
        self.save()

    def get_absolute_url(self):
        return reverse('post_list')

    def __str__(self):
        return self.text


class Likes(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)

    def get_absolute_url(self):
        return reverse('post_list')

    def __str__(self):
        return self.post.text
