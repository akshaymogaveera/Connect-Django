import base64
import json

import jsonschema
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required  # login decorator that makes it easier
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
#
from django.views.decorators.cache import cache_control
from django.views.generic import (TemplateView, ListView,
                                  DetailView, CreateView,
                                  UpdateView, DeleteView)
from jsonschema import ValidationError, Draft3Validator
from jsonschema.validators import validator_for
from numpy import unicode
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from firstapp.Operations.serializers import *
from firstapp.Operations.validation import *
from firstapp.Operations.friendsOps import *
from firstapp.forms import UserProfileInfoForm, UserForm, PostForm
from .Operations import friendsOps
from .models import UserProfileInfo, Friends, Post, Comment, Likes


def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)


def liked_by_user(request, pk):
    data = {
        'is_taken': Likes.objects.filter(post=pk, person=request.user).exists()
    }
    return JsonResponse(data)


def special(request):
    # Remember to also set login url in settings.py!
    # LOGIN_URL = '/basic_app/user_login/'
    return HttpResponse("You are logged in. Nice!")


# Note here that inside of our user_logout function, there is no checking if the user is logged in or not
# the beauty of django is that to do so, you just have to use the decorator login_required. AND THAT IS IT! beautiful.
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def register(request):
    registered = False

    if request.method == 'POST':

        # Get info from "both" forms
        # It appears as one form to the user on the .html page
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)

        # Check to see both forms are valid
        if user_form.is_valid() and profile_form.is_valid():

            # Save User Form to Database
            user = user_form.save()

            # Hash the password
            user.set_password(user.password)

            # Update with Hashed password
            user.save()

            # Now we deal with the extra info!

            # Can't commit yet because we still need to manipulate
            profile = profile_form.save(commit=False)

            # Set One to One relationship between
            # UserForm and UserProfileInfoForm
            profile.user = user

            # Check if they provided a profile picture
            if 'profile_pic' in request.FILES:
                print('found it')
                # If yes, then grab it from the POST form reply
                profile.profile_pic = request.FILES['profile_pic']

            # Now save model
            profile.save()

            # Registration Successful!
            registered = True

        else:
            # One of the forms was invalid if this else gets called.
            print(user_form.errors, profile_form.errors)

    else:
        # Was not an HTTP post so we just render the forms as blank.
        user_form = UserForm()
        profile_form = UserProfileInfoForm()

    # This is the render and context dictionary to feed
    # back to the registration.html file page.
    return render(request, 'firstapp/registration.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})


'''
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # this get will grab it from the HTML
        password = request.POST.get('password')

        user = authenticate(username=username,
                            password=password)  # user is a boolean that tells us if it is authenticated or not
        if user:
            if user.is_active:
                login(request, user)
                # return HttpResponseRedirect(reverse('index')) #if its everything ok with the login and passwrd, you will log in and be redirected to the index page
                # return redirect('firstapp:profile',usrname=username)
                return redirect('firstapp:news_feed')
            else:
                return HttpResponse("ACCOUNT NOT ACTIVE!")
        else:
            print("LOGIN FAILED!")
            print("Username: {} and password {}".format(username, password))
            # return HttpResponse("Invalid login details supplied!")
            messages.error(request, 'Invalid credentials')
            return redirect('firstapp:user_login')
    else:
        return render(request, 'firstapp/login.html', {})
'''


@login_required
def profile(request, usrname):
    user = User.objects.get(username=usrname)
    try:
        friends_count = Friends.objects.filter(user1=request.user, friend_status=2).count()
    except:
        friends_count = None
    try:
        friends_other_count = Friends.objects.filter(user1=user, friend_status=2).count()
    except:
        friends_other_count = None
    try:
        userinfo = UserProfileInfo.objects.get(user=user.id)

    except:
        userinfo = None

    try:
        posts = Post.objects.filter(author=user.id).order_by('created_date')
    except:
        posts = None

    try:
        friends_info = Friends.objects.get(user1=request.user.id, user2=user.id)


    except:
        friends_info = None

    try:
        friend_request = Friends.objects.get(user2=request.user.id, user1=user.id)
    except:
        friend_request = None

    return render(request, 'firstapp/profile.html',
                  {"friends_other_count": friends_other_count, "friends_count": friends_count, "user_profile": user,
                   'userinfo': userinfo, 'posts': posts, 'friends_info': friends_info,
                   'friend_request': friend_request})


'''
@login_required
def search(request):
    if request.method=='POST':
        user_result2,friends_result,friend_request_result=[],[],[]
        username=request.POST.get('username')
        if len(username)>0:
            userres=User.objects.filter(username__icontains=username).exclude(id=request.user.id)
            if userres:
                for users in userres:
                    try:
                        userinfo1=UserProfileInfo.objects.get(user=users.id)
                    except:
                        userinfo1=None
                    try:
                        friends_info=Friends.objects.get(user1=request.user.id,user2=users.id)
                    except:
                        friends_info=None
                    try:
                        friend_request=Friends.objects.get(user2=request.user.id,user1=users.id)
                    except:
                        friend_request=None
                    user_result2.append(userinfo1)
                    friends_result.append(friends_info)
                    friend_request_result.append(friend_request)

                result=zip(userres,user_result2,friends_result,friend_request_result)
                return render(request,'firstapp/search.html',{'result':result})
            else:
                #return HttpResponse("Invalid details supplied!")
                messages.error(request,'Invalid details')
                return render(request,'firstapp/search.html')
        else:
                #return HttpResponse("Invalid details supplied!")
                messages.error(request,'Please enter username')
                return render(request,'firstapp/search.html')
    return render(request,'firstapp/profile.html',{"user":user,'userinfo':userinfo})
'''


@login_required
def add_friend(request, pk):
    another_user = get_object_or_404(User, pk=pk)
    current_user = get_object_or_404(User, pk=request.user.id)
    friend, created = Friends.objects.get_or_create(user1=current_user, user2=another_user)

    friend_stat = friend.friend_status
    if friend_stat == 0:
        friend.friend_status = 1
        friend.save()
    elif (friend_stat == 1):
        friend.friend_status = 2
        friend.save()

    return JsonResponse({})


@login_required
def accept_friend(request, pk):
    sentby = get_object_or_404(User, pk=pk)
    acceptedby = get_object_or_404(User, pk=request.user.id)
    friend, created = Friends.objects.get_or_create(user1=sentby, user2=acceptedby)
    friend_stat = friend.friend_status
    if friend_stat == 0:
        friend.friend_status = 1
        friend.save()
    elif (friend_stat == 1):
        friend.friend_status = 2
        replica = Friends(user1=acceptedby, user2=sentby, friend_status=2)
        friend.save()
        replica.save()
    return JsonResponse({})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def delete_friend(request, pk):
    user_1 = get_object_or_404(User, pk=pk)
    user_2 = get_object_or_404(User, pk=request.user.id)
    Friends.objects.filter(user1=user_1, user2=user_2, friend_status=2).delete()
    Friends.objects.filter(user1=user_2, user2=user_1, friend_status=2).delete()
    return JsonResponse({})


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class FriendListView(LoginRequiredMixin, ListView):
    model = Friends

    def get_queryset(self, **kwargs):  # use orm
        return Friends.objects.filter(user1=self.kwargs['pk'], friend_status=2)


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class LikesListView(LoginRequiredMixin, ListView):
    model = Likes

    def get_queryset(self, **kwargs):  # use orm
        return Likes.objects.filter(post=self.kwargs['pk'])


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class FriendDetailView(LoginRequiredMixin, TemplateView):
    # context_object_name='userprofileinfo_detail'
    template_name = 'firstapp/userprofileinfo_detail.html'
    pk = None

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(FriendDetailView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        userinfo = UserProfileInfo.objects.filter(user=self.kwargs['pk'])
        context['userinfo'] = userinfo
        return context


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class FriendReqListView(LoginRequiredMixin, TemplateView):
    model = Friends
    context_object_name = 'friend_req_list'
    template_name = 'firstapp/friend_req_list.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(FriendReqListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        friend_req_list = Friends.objects.filter(user2=self.request.user, friend_status=1)
        posts = Post.objects.filter(author=self.request.user).order_by('-created_date')
        comment_noti, likes_noti, pts = [], [], []
        for p in posts:
            try:
                likes = Likes.objects.filter(post=p.id).order_by('-created_date')
            except:
                likes = None
            try:
                comment = Comment.objects.filter(post=p.id).order_by('-created_date')
            except:
                comment = None
            likes_noti.append(likes)
            comment_noti.append(comment)

        context['likes_noti'] = likes_noti
        context['comment_noti'] = comment_noti
        context['friend_req_list'] = friend_req_list
        return context


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class PostListView(LoginRequiredMixin, ListView):
    login_url = '/firstappuser_login/'
    model = Post

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user.id).order_by('created_date')


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class NewsFeedPostListView(LoginRequiredMixin, ListView):
    login_url = '/firstappuser_login/'
    model = Post
    template_name = 'firstapp/post_news_feed.html'

    def get_queryset(self):
        friends = Friends.objects.filter(user1=self.request.user, friend_status=2)
        friends_id = [i.user2.id for i in friends]

        return Post.objects.filter(author__in=friends_id).order_by('-created_date')


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class PostDetailView(LoginRequiredMixin, DetailView):
    login_url = '/firstappuser_login/'
    model = Post


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class CreatePostView(LoginRequiredMixin, CreateView):
    login_url = '/firstappuser_login/'
    template_name = 'firstapp/post_form.html'
    form_class = PostForm
    model = Post

    def form_valid(self, form):
        form = self.form_class(self.request.POST, self.request.FILES)
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        # article.save()  # This is redundant, see comments.
        return super(CreatePostView, self).form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse_lazy('firstapp:profile', kwargs={'usrname': self.request.user.username})


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/firstappuser_login/'
    form_class = PostForm
    model = Post

    def get_success_url(self, **kwargs):
        return reverse_lazy('firstapp:profile', kwargs={'usrname': self.request.user.username})


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch')
class PostDeleteView(LoginRequiredMixin, DeleteView):
    login_url = '/firstappuser_login/'
    model = Post

    def get_success_url(self, **kwargs):
        return reverse_lazy('firstapp:profile', kwargs={'usrname': self.request.user.username})


'''
@login_required
def add_comment_to_post(request,pk):
    post=get_object_or_404(Post,pk=pk)
    if request.method=='POST':
        form=CommentForm(request.POST)
        if form.is_valid():
            comment=form.save(commit=False)
            comment.post=post
            comment.author=request.user
            comment.save()
            return redirect('firstapp:profile',usrname=request.user.username)
    else:
        form=CommentForm()
    return render(request,'firstapp/comment_form.html',{'form':form})
'''


@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post_text = request.POST.get('the_post')
        comment = Comment.objects.create(post=post, author=request.user, text=post_text)
        comment.save()
    return JsonResponse({})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('firstapp:profile', usrname=request.user.username)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('firstapp:profile', usrname=request.user.username)


@login_required
def like_post(request, pk):
    post = Post.objects.get(pk=pk)
    like, created = Likes.objects.get_or_create(post=post, person=request.user)

    like.save()

    return JsonResponse({})


@login_required
def unlike_post(request, pk):
    try:
        Likes.objects.filter(post=pk, person=request.user).delete()
    except:
        print("no likes")

    return JsonResponse({})


@login_required
def count_likes(request, pk):
    data = {
        'likes': Likes.objects.filter(post=pk).count()
    }
    return JsonResponse(data)
