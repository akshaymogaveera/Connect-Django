from django import forms
from django.contrib.auth.models import User
from firstapp.models import UserProfileInfo,Post,Comment

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username','first_name','last_name','email','password')

class UserProfileInfoForm(forms.ModelForm):
    class Meta():
        model = UserProfileInfo
        fields = ('portfolio_site','profile_pic','city','state','country','school','college','sex')

class PostForm(forms.ModelForm):


    class Meta():
        model=Post
        fields=('text','post_pics')

        widgets={

        'text':forms.Textarea(attrs={'class':'editable medium-editor-textarea postcontent'}),

        }


'''
class CommentForm(forms.ModelForm):

    class Meta():
        model=Comment
        fields=('text',)

        widgets={


        'text':forms.Textarea(attrs={'class':'editable medium-editor-textarea'}),

        }
'''