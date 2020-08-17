from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from firstapp.models import UserProfileInfo, Friends, Post, Comment, Likes, User


class UserGetMainSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class PostGetSerializer(serializers.ModelSerializer):
    author = UserGetMainSerializer(many=False, read_only=True)

    class Meta:
        model = Post
        fields = '__all__'


class PostSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class UserProfileInfoGetSerializer(serializers.ModelSerializer):
    user = UserGetMainSerializer(many=False)

    class Meta:
        model = UserProfileInfo
        fields = '__all__'


class UserProfileInfoSaveSerializer(serializers.ModelSerializer):
    user = UserGetMainSerializer(many=False)

    class Meta:
        model = UserProfileInfo
        fields = '__all__'


class FriendsGetSerializer(serializers.ModelSerializer):
    user1 = UserGetMainSerializer(many=False)
    user2 = UserGetMainSerializer(many=False)

    class Meta:
        model = Friends
        fields = '__all__'


class FriendsSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friends
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],

        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LikesGetSerializer(serializers.ModelSerializer):
    person = UserGetMainSerializer(many=False)

    class Meta:
        model = Likes
        fields = '__all__'


class LikesSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Likes
        fields = '__all__'


class CommentGetSerializer(serializers.ModelSerializer):
    author = UserGetMainSerializer(many=False)

    class Meta:
        model = Comment
        fields = '__all__'


class CommentSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class UserGetProfilePicSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileInfo
        fields = ['profile_pic']
