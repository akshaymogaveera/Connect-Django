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


class ValidateToken(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            if self.request.user:
                self.refresh, self.access_token = validateUser.getToken(self.request.user)
                return JsonResponse({'refresh': self.refresh, 'access': self.access_token, 'id': self.request.user.id})
            else:
                return JsonResponse({'status': 'Failed', 'message': "Authentication Failed"}, status=401)
        except:
            return JsonResponse({'status': 'Failed'}, status=400)


class AuthenticateUserApi(APIView):
    # permission_classes = (IsAuthenticated,)
    def post(self, request):
        try:
            self.username = str(request.POST['username'])
            self.password = str(request.POST['password'])
            self.user = validateUser.authenticateUser(self.username, self.password)
            if self.user:
                self.refresh, self.access_token = validateUser.getToken(self.user)
                return JsonResponse({'refresh': self.refresh, 'access': self.access_token, 'id': self.user.id})
            else:
                return JsonResponse({'status': 'Failed', 'message': "Authentication Failed"}, status=400)
        except:
            return JsonResponse({'status': 'Failed', 'message': "Authentication Failed"}, status=400)


class BasicAuthenticateUserApi(APIView):
    # permission_classes = (IsAuthenticated,)
    def post(self, request):
        try:
            auth_header = request.META['HTTP_AUTHORIZATION']
            encoded_credentials = auth_header.split(' ')[1]  # Removes "Basic " to isolate credentials
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8").split(':')
            self.username = unicode(decoded_credentials[0])
            self.password = unicode(decoded_credentials[1])

            self.user = validateUser.authenticateUser(self.username, self.password)
            if self.user:
                self.refresh, self.access_token = validateUser.getToken(self.user)
                return JsonResponse({'refresh': self.refresh, 'access': self.access_token, 'id': self.user.id})
            else:
                return JsonResponse({'status': 'Failed', 'message': "Authentication Failed"}, status=400)
        except:
            return JsonResponse({'status': 'Failed', 'message': "Authentication Failed"}, status=400)


class NewsFeedPost(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            self.friends = Friends.objects.filter(user1=self.request.user, friend_status=2)
            self.friends_id = [i.user2.id for i in self.friends]
            serializer = PostGetSerializer(Post.objects.filter(author__in=self.friends_id).order_by('-created_date'),
                                           many=True)
            return Response(serializer.data)
        except:
            return JsonResponse({'status': 'Failed'}, status=400)


class UserProfile(APIView):
    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        self.self = False
        try:
            validator = IdValidator().validate(request.data)
            validaction = validator[0]

            if validaction:
                self.user_id = str(request.data['id'])
                status, requested_user = validation.validateUser.validateAndGetUser(self.user_id)

                if status:

                    self.serializer = UserProfileInfoGetSerializer(UserProfileInfo.objects.get(user=requested_user))

                    if requested_user.id == request.user.id:
                        self.self = True

                    return JsonResponse({'info': self.serializer.data, 'self': self.self}, status=200)
                else:
                    return JsonResponse({"error": "Invalid ID passed"})

            else:
                return JsonResponse({"error": validator[1]})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class UserMainInfo(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        self.self = False
        try:
            validator = IdValidator().validate(request.data)
            validaction = validator[0]

            if validaction:
                self.user_id = str(request.data['id'])
                status, requested_user = validation.validateUser.validateAndGetUser(self.user_id)

                if status:

                    self.serializer = UserGetMainSerializer(User.objects.get(id=requested_user.id))

                    if requested_user.id == request.user.id:
                        self.self = True

                    return JsonResponse({'info': self.serializer.data, 'self': self.self}, status=200)
                else:
                    return JsonResponse({"error": "Invalid ID passed"})

            else:
                return JsonResponse({"error": validator[1]})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class UserGetProfilePic(APIView):
    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        self.self = False
        try:
            validator = IdValidator().validate(request.data)
            validaction = validator[0]

            if validaction:
                self.user_id = str(request.data['id'])
                status, requested_user = validation.validateUser.validateAndGetUser(self.user_id)

                if status:

                    self.serializer = UserGetProfilePicSerializer(UserProfileInfo.objects.get(user=requested_user))

                    return Response(self.serializer.data, status=200)
                else:
                    return JsonResponse({"error": "Invalid ID passed"})

            else:
                return JsonResponse({"error": validator[1]})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class UserFeed(APIView):
    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        self.self = False
        try:
            validator = IdValidator().validate(request.data)
            validaction = validator[0]

            if validaction:

                self.user_id = str(request.data['id'])
                status, requested_user = validation.validateUser.validateAndGetUser(self.user_id)

                if status:
                    self.serializer = PostGetSerializer(
                        Post.objects.filter(author=requested_user.id).order_by('-created_date'),
                        many=True)
                    if requested_user.id == request.user.id:
                        self.self = True

                    return Response(self.serializer.data)

                    # return JsonResponse({'userfeed': self.serializer.data, 'self': self.self}, status=200)

                else:
                    return JsonResponse({"error": "Invalid ID passed"}, status=400)
            else:
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class FriendsList(APIView):
    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        self.self = False
        try:
            validator = IdValidator().validate(request.data)
            validaction = validator[0]

            if validaction:

                self.user_id = str(request.data['id'])
                status, requested_user = validation.validateUser.validateAndGetUser(self.user_id)

                if status:

                    self.serializer = FriendsGetSerializer(
                        Friends.objects.filter(user1=requested_user.id, friend_status=2),
                        many=True)
                    if requested_user.id == request.user.id:
                        self.self = True

                    return JsonResponse({'FriendsList': self.serializer.data, 'self': self.self}, status=200)
                else:
                    return JsonResponse({"error": "Invalid ID passed"})
            else:
                return JsonResponse({"error": validator[1]})

        except Exception as e:

            return JsonResponse({"error": str(e)}, status=400)


class FriendRequest(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            self.serializer = FriendsGetSerializer(Friends.objects.filter(user2=self.request.user, friend_status=1),
                                                   many=True)
            return Response(self.serializer, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class Register(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, *args, **kwargs):

        try:

            validator = RegisterValidate().validate(request.data)

            if validator[0]:
                self.data = request.data.copy()
                status, self.user, self.myResponse = Registration().userValidate(request.data)

                print(status, self.myResponse)
                if status:
                    self.data['user'] = self.user.id
                    userprofile = UserProfileInfoSaveSerializer(data=self.data)
                    if userprofile.is_valid():
                        userprofile.save()
                        self.myResponse["userprofile"] = userprofile.data
                    else:
                        Registration.deleteUser(self.user)
                        self.myResponse = {"userprofile_error": userprofile.errors}

                if validator[1] is None:
                    error = self.myResponse
                else:
                    error = {**validator[1], **self.myResponse}
                return JsonResponse({"error": error}, status=400)

            else:
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            return JsonResponse({"user_error": str(e)}, status=400)


class RegisterUpdate(APIView):
    parser_classes = (MultiPartParser,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:

            self.data = request.data.copy()
            if str(User.objects.get(id=self.request.user.id).email) == str(request.data['email']):
                self.data['email'] = "sameEmail"
            validator = RegisterUpdateValidate().validate(self.data)
            print(request.data)
            if validator[0]:

                user = User.objects.get(id=self.request.user.id)
                userinfo = UserProfileInfo.objects.get(user=self.request.user)
                if 'country' in request.data:
                    userinfo.country = request.data['country']
                if 'city' in request.data:
                    print(request.data['city'])
                    userinfo.city = request.data['city']
                if 'profile_pic' in request.data:
                    userinfo.profile_pic = request.data['profile_pic']
                if 'email' in request.data:
                    if str(user.email) != str(request.data['email']):
                        user.email = request.data['email']

                userinfo.save()
                user.save()

                return Response(UserProfileInfoGetSerializer(userinfo).data, status=200)


            else:
                print(validator[1])
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            print(e.with_traceback())
            return JsonResponse({"error": str(e)}, status=400)


class Friend(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        self.self = False
        try:

            print(request.data)
            validator = FriendActionValidator().validate(request.data)
            validaction = validator[0]
            if validaction:

                self.user_id = str(request.data['id'])
                self.action = str(request.data['action'])

                status, user2 = validation.validateUser.validateAndGetUser(self.user_id)

                if status and self.user_id != str(request.user.id):

                    '''
                     100 -- Request sent from user 1 to 2
                     101 -- Already friends
                     102 -- Accepted friend request
                     103 -- Unusual row was present so deleted the row
                     104 -- Unusual row was present so fixed the row
                     105 -- Request already sent 
                     200 -- No User Found
                     201 -- Exception
                    '''
                    if self.action == "add":
                        status, response = friendsOps.FriendOperations.addFriend(request.user, user2)
                        '''
                         300 -- Weren't friends
                         301 -- Successfully Deleted
                         303 -- Unusual row was present so deleted the row
                         200 -- No User Found
                         201 -- Exception
                        '''

                    elif self.action == "delete":
                        status, response = friendsOps.FriendOperations.deleteFriend(request.user, user2)

                    return JsonResponse({'status': status, 'response': response})

                elif status and self.user_id == str(request.user.id):

                    return JsonResponse({"error": " Cannot add friend to self "})


                else:
                    return JsonResponse({"error": "Invalid ID"}, status=400)

            else:
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:

            return JsonResponse({"error": str(e)}, status=400)


class FriendStatus(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        self.status = -1
        try:

            validator = IdValidator().validate(request.data)
            validaction = validator[0]
            if validaction:

                self.user_id = str(request.data['id'])

                status, user2 = validation.validateUser.validateAndGetUser(self.user_id)

                if status and self.user_id != str(request.user.id):

                    status12 = Friends.objects.filter(user1=self.request.user, user2=user2).exists()
                    status21 = Friends.objects.filter(user1=user2, user2=self.request.user).exists()

                    if status12:
                        friendstat12 = Friends.objects.get(user1=self.request.user, user2=user2)
                        self.status = friendstat12.friend_status

                    elif status21:
                        friendstat21 = Friends.objects.get(user1=user2, user2=self.request.user)

                        if friendstat21.friend_status == 1:
                            self.status = 3
                        else:
                            self.status = friendstat21.friend_status

                    return JsonResponse({'status': self.status})

                elif status and self.user_id == str(request.user.id):

                    return JsonResponse({"error": " Cannot add friend to self "}, status=400)


                else:
                    return JsonResponse({"error": "Invalid ID"}, status=400)

            else:
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:

            return JsonResponse({"error": str(e)}, status=400)


class FriendCount(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            FriendsCount = Friends.objects.filter(user1=self.request.user, friend_status=2).count()

            return JsonResponse({"count": FriendsCount}, status=200)


        except Exception as e:
            print(e.with_traceback())
            return JsonResponse({"count": "error"}, status=400)

    def post(self, request):
        try:
            validator = IdValidator().validate(request.data)
            validaction = validator[0]

            if validaction:

                self.user_id = str(request.data['id'])
                status, requested_user = validation.validateUser.validateAndGetUser(self.user_id)

                if status:
                    FriendsCount = Friends.objects.filter(user1=requested_user, friend_status=2).count()

                    return JsonResponse({"count": FriendsCount}, status=200)



                else:
                    return JsonResponse({"error": "Invalid ID passed"}, status=400)
            else:
                return JsonResponse({"count": "error"}, status=400)


        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class Posts(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def get(self, request, *args, **kwargs):

        try:
            validator = IdValidator().validate(request.data)

            if validator[0]:
                print(request.data)
                self.post_id = str(request.data['id'])
                status, post = validation.validateUser.validateAndGetPost(self.post_id)

                if status:
                    return Response(PostGetSerializer(post).data, status=200)
                else:
                    return JsonResponse({"error": "Invalid ID passed"}, status=400)

            else:
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            return JsonResponse({"user_error": str(e)}, status=400)

    def put(self, request, *args, **kwargs):

        try:
            validator = PostUpdateValidator().validate(request.data)
            if validator[0]:

                self.post_id = str(request.data['id'])
                status, post = validation.validateUser.validateAndGetPost(self.post_id)

                if status:
                    if 'post_pics' in request.data:
                        post.post_pics = request.data['post_pics']
                    if 'text' in request.data:
                        post.text = request.data['text']

                    post.save()

                    return Response(PostGetSerializer(post).data, status=200)
                else:
                    return JsonResponse({"error": "Invalid ID passed"}, status=400)



            else:
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            print(e.with_traceback())
            return JsonResponse({"user_error": str(e)}, status=400)

    def post(self, request, *args, **kwargs):
        self.myResponse = None
        try:

            validator = PostValidator().validate(request.data)
            # print(request.data['text'])
            if validator[0]:

                self.data = request.data.copy()
                self.data['author'] = self.request.user.id
                createpost = PostSaveSerializer(data=self.data)

                if createpost.is_valid():
                    createpost.save()

                    self.myResponse = {"createpost": createpost.data}
                else:
                    print(createpost.errors)
                    self.myResponse = {"createpost_error": createpost.errors}

                return JsonResponse(self.myResponse)

            else:
                print(validator[1])
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            print(e.with_traceback())
            return JsonResponse({"user_error": str(e)}, status=400)


class PostDelete(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        try:
            print(request.data)
            validator = IdValidator().validate(request.data)

            if validator[0]:

                self.post_id = str(request.data['id'])
                status, post = validation.validateUser.validateAndGetPost(self.post_id)

                if status:

                    post.delete()

                    return Response(PostGetSerializer(post).data, status=200)
                else:
                    print(status)
                    return JsonResponse({"error": "Invalid ID passed"}, status=400)



            else:
                print(validator[1])
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            print(e.with_traceback())
            return JsonResponse({"post_error": str(e)}, status=400)


class getLiked(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            validator = IdValidator().validate(request.data)
            if validator[0]:

                self.post_id = str(request.data['id'])
                status, post = validation.validateUser.validateAndGetPost(self.post_id)

                if status:

                    if Likes.objects.filter(post=post, person_id=self.request.user.id).exists():
                        response = {"liked": "True", "UserID": self.request.user.id}
                    else:
                        response = {"liked": "False", "UserID": self.request.user.id}

                    return JsonResponse(response, status=200)
                else:
                    return JsonResponse({"error": "Invalid ID passed"}, status=400)



            else:
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            return JsonResponse({"user_error": str(e)}, status=400)


class Like(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            validator = IdValidator().validate(request.data)
            if validator[0]:

                self.post_id = str(request.data['id'])
                status, post = validation.validateUser.validateAndGetPost(self.post_id)

                if status:

                    if Likes.objects.filter(post=post, person_id=self.request.user.id).exists():
                        response = {"liked": "True", "UserID": self.request.user.id}
                    else:
                        response = {"liked": "False", "UserID": self.request.user.id}

                    return JsonResponse(response, status=200)
                else:
                    return JsonResponse({"error": "Invalid ID passed"}, status=400)



            else:
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            return JsonResponse({"user_error": str(e)}, status=400)

    def post(self, request):
        try:
            validator = IdValidator().validate(request.data)
            if validator[0]:

                self.post_id = str(request.data['id'])
                status, post = validation.validateUser.validateAndGetPost(self.post_id)

                if status:

                    if Likes.objects.filter(post=post, person_id=self.request.user.id).exists():
                        like = Likes.objects.get(post=post, person_id=self.request.user.id)
                        like.delete()
                    else:
                        like = Likes.objects.create(post=post, person_id=self.request.user.id)

                    return Response(LikesGetSerializer(like).data, status=200)
                else:
                    return JsonResponse({"error": "Invalid ID passed"}, status=400)

            else:
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            return JsonResponse({"user_error": str(e)}, status=400)


class PostCount(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            PostCount = Post.objects.filter(author=self.request.user).count()

            return JsonResponse({"count": PostCount}, status=200)


        except Exception as e:
            print(e.with_traceback())
            return JsonResponse({"count": "error"}, status=400)

    def post(self, request):
        self.self = False
        try:
            validator = IdValidator().validate(request.data)
            validaction = validator[0]

            if validaction:

                self.user_id = str(request.data['id'])
                status, requested_user = validation.validateUser.validateAndGetUser(self.user_id)

                if status:
                    PostCount = Post.objects.filter(author=requested_user).count()

                    return JsonResponse({"count": PostCount}, status=200)

                    # return JsonResponse({'userfeed': self.serializer.data, 'self': self.self}, status=200)

                else:
                    return JsonResponse({"error": "Invalid ID passed"}, status=400)
            else:
                return JsonResponse({"count": "error"}, status=400)


        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class PostLikesCount(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            print(str(request.data) + "  ++++++  ")
            validator = IdValidator().validate(request.data)
            if validator[0]:

                self.post_id = str(request.data['id'])
                status, post = validation.validateUser.validateAndGetPost(self.post_id)

                if status:

                    LikesCount = Likes.objects.filter(post=post).count()

                    return JsonResponse({"count": LikesCount}, status=200)
                else:
                    return JsonResponse({"error": "Invalid ID passed"}, status=400)

            else:
                print(validator[1])
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            print(e.with_traceback())
            return JsonResponse({"user_error": str(e)}, status=400)


class PostLikesList(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            validator = IdValidator().validate(request.data)
            if validator[0]:

                self.post_id = str(request.data['id'])
                status, post = validation.validateUser.validateAndGetPost(self.post_id)

                if status:

                    like = LikesGetSerializer(
                        Likes.objects.filter(post=post).order_by('created_date'),
                        many=True)
                    return Response(like.data, status=200)
                else:
                    return JsonResponse({"error": "Invalid ID passed"}, status=400)

            else:
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            return JsonResponse({"user_error": str(e)}, status=400)


class PostCommentsList(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            validator = IdValidator().validate(request.data)
            if validator[0]:

                self.post_id = str(request.data['id'])
                status, post = validation.validateUser.validateAndGetPost(self.post_id)

                if status:

                    comment = CommentGetSerializer(
                        Comment.objects.filter(post=post).order_by('created_date'),
                        many=True)

                    return Response(comment.data, status=200)
                else:
                    return JsonResponse({"error": "Invalid ID passed"}, status=400)

            else:
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            return JsonResponse({"user_error": str(e)}, status=400)


class PostCommentsCount(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            validator = IdValidator().validate(request.data)
            if validator[0]:

                self.post_id = str(request.data['id'])
                status, post = validation.validateUser.validateAndGetPost(self.post_id)

                if status:

                    commentCount = Comment.objects.filter(post=post).count()

                    return JsonResponse({"count": commentCount}, status=200)
                else:
                    return JsonResponse({"error": "Invalid ID passed"}, status=400)

            else:
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            return JsonResponse({"user_error": str(e)}, status=400)


class Comments(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            validator = CommentValidator().validate(request.data)
            if validator[0]:

                self.post_id = str(request.data['id'])
                self.text = str(request.data['text'])
                status, post = validation.validateUser.validateAndGetPost(self.post_id)

                if status:

                    comment = Comment.objects.create(post=post, author=self.request.user, text=self.text,
                                                     approved_comment=True)

                    return Response(CommentGetSerializer(comment).data, status=200)
                else:
                    return JsonResponse({"error": "Invalid ID passed"}, status=400)

            else:
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            return JsonResponse({"user_error": str(e)}, status=400)

    def delete(self, request, *args, **kwargs):

        try:
            validator = IdValidator().validate(request.data)

            if validator[0]:

                self.comment_id = str(request.data['id'])
                status, comment = validation.validateUser.validateAndGetComment(self.comment_id)

                if status:

                    post = Post.objects.get(id=comment.post.id)
                    if self.request.user == comment.author or self.request.user == post.author:
                        comment.delete()
                    else:
                        return JsonResponse({"error": "Comment doesn't belong to requested User or Post"}, status=400)

                    return Response(CommentGetSerializer(comment).data, status=200)
                else:
                    return JsonResponse({"error": "Invalid ID passed "}, status=400)



            else:
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            return JsonResponse({"post_error": str(e)}, status=400)

    def put(self, request):
        try:
            validator = CommentValidator().validate(request.data)

            if validator[0]:
                self.comment_id = str(request.data['id'])
                self.text = str(request.data['text'])
                status, comment = validation.validateUser.validateAndGetComment(self.comment_id)

                if status:

                    if self.request.user == comment.author:
                        comment.text = self.text
                        comment.save()
                    else:
                        return JsonResponse({"error": "Comment doesn't belong to requested User or Post"}, status=400)

                    return Response(CommentGetSerializer(comment).data, status=200)
                else:
                    return JsonResponse({"error": "Invalid ID passed "}, status=400)

            else:
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            return JsonResponse({"post_error": str(e)}, status=400)


class MutualFriendsList(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            validator = IdValidator().validate(request.data)
            if validator[0]:

                self.user_id = str(request.data['id'])
                status, user2 = validation.validateUser.validateAndGetUser(self.user_id)

                if status:

                    if self.request.user != user2:
                        friendsUser = Friends.objects.filter(user1=self.request.user, friend_status=2)
                        friendsUserId = [i.user2.id for i in friendsUser]

                        friendsOtherUser = Friends.objects.filter(user1=user2, friend_status=2)
                        friendsOtherUserId = [i.user2.id for i in friendsOtherUser]

                        mutualFriends = list(set(friendsUserId).intersection(friendsOtherUserId))

                        self.count = User.objects.filter(id__in=mutualFriends).count()

                        return JsonResponse({"count": self.count}, status=200)

                    else:
                        return JsonResponse({"error": "ID passed is self"}, status=400)

                else:
                    return JsonResponse({"error": "Invalid ID passed"}, status=400)

            else:
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            return JsonResponse({"user_error": str(e)}, status=400)

    def post(self, request):
        try:
            validator = IdValidator().validate(request.data)
            if validator[0]:

                self.user_id = str(request.data['id'])
                status, user2 = validation.validateUser.validateAndGetUser(self.user_id)

                if status:

                    if self.request.user != user2:
                        friendsUser = Friends.objects.filter(user1=self.request.user, friend_status=2)
                        friendsUserId = [i.user2.id for i in friendsUser]

                        friendsOtherUser = Friends.objects.filter(user1=user2, friend_status=2)
                        friendsOtherUserId = [i.user2.id for i in friendsOtherUser]

                        mutualFriends = list(set(friendsUserId).intersection(friendsOtherUserId))

                        self.serializer = UserGetMainSerializer(User.objects.filter(id__in=mutualFriends), many=True)

                        return Response(self.serializer.data, status=200)

                    else:
                        return JsonResponse({"error": "ID passed is self"}, status=400)
                else:
                    return JsonResponse({"error": "Invalid ID passed"}, status=400)

            else:
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            return JsonResponse({"user_error": str(e)}, status=400)


class Search(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            print(request.data)
            validator = SearchValidate().validate(request.data)
            validaction = validator[0]
            if validaction:

                self.input = str(request.data['input'])
                self.input_split = self.input.split()

                print(self.input_split[0])
                if len(self.input_split) >= 2:
                    result = User.objects.filter(first_name__contains=self.input_split[0],
                                                 last_name__contains=self.input_split[1])
                elif len(self.input_split) == 1:
                    result = User.objects.filter(first_name__contains=self.input_split[0])
                    result = result | User.objects.filter(username__icontains=self.input_split[0])
                    result = result | User.objects.filter(last_name__contains=self.input_split[0])

                    print(result)

                return Response(UserGetMainSerializer(result, many=True).data, status=200)


            else:
                print(validator[1])
                return JsonResponse({"error": validator[1]}, status=400)

        except Exception as e:
            print(e.with_traceback())
            return JsonResponse({"error": str(e)}, status=400)


class LatestLikeOfPost(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        try:

            posts = Post.objects.filter(author=self.request.user)
            response = {post.id: [Likes.objects.filter(post=post.id).last().person.id,
                                  Likes.objects.filter(post=post.id).last().person.username, str(post.post_pics),
                                  Likes.objects.filter(post=post.id).count() - 1] for post in posts if
                        Likes.objects.filter(post=post.id).last()}

            return JsonResponse(response, status=200, safe=True)


        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class LatestCommentsOfPost(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        try:

            posts = Post.objects.filter(author=self.request.user)
            response = {post.id: [Comment.objects.filter(post=post.id).last().author.id,
                                  Comment.objects.filter(post=post.id).last().author.username, str(post.post_pics),
                                  Comment.objects.filter(post=post.id).count() - 1] for post in posts if
                        Comment.objects.filter(post=post.id).last()}

            return JsonResponse(response, status=200, safe=True)


        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
