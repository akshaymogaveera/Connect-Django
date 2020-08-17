from django.contrib import admin
from firstapp.models import UserProfileInfo,Friends,Post,Comment,Likes

# Register your models here.
admin.site.register(UserProfileInfo)
admin.site.register(Friends)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Likes)