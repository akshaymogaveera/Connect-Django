from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
import json

from incoming import datatypes, PayloadValidator
from firstapp.Operations.serializers import UserSerializer
from firstapp.models import User, Post, Comment


class validateUser():
    @staticmethod
    def authenticateUser(username, password):
        if (username is not None and password is not None and len(username) > 4 and len(
                password) > 4 and username.isalnum() and password.isalnum()):
            user = authenticate(username=username, password=password)
            return user
        else:
            return None

    @staticmethod
    def getToken(user):
        if user:
            if user.is_active:
                refresh = RefreshToken.for_user(user)
                return str(refresh), str(refresh.access_token)
            else:
                return [None, None]

    @staticmethod
    def validateEmail(email):
        return User.objects.filter(email=email).exists()

    @staticmethod
    def validateAndGetUser(id):
        if User.objects.filter(id=id).exists():
            return True, User.objects.get(id=id)
        else:
            return False, None

    @staticmethod
    def validateAndGetPost(id):
        if Post.objects.filter(id=id).exists():
            return True, Post.objects.get(id=id)
        else:
            return False, None

    @staticmethod
    def validateAndGetComment(id):
        if Comment.objects.filter(id=id).exists():
            return True, Comment.objects.get(id=id)
        else:
            return False, None


class Registration:
    def userValidate(self, data):
        self.status = False
        self.user = None
        userserializer = UserSerializer(data=data)
        if userserializer.is_valid():
            try:
                self.user = userserializer.save()
                if self.user:
                    self.status = True
                    self.myresponse = {"user": userserializer.data}
            except Exception as e:
                self.myresponse = str(e)
        else:
            self.myresponse = userserializer.errors

        return self.status, self.user, self.myresponse

    @staticmethod
    def deleteUser(user):
        User.objects.get(id=user.id).delete()


class FriendActionValidator(PayloadValidator):
    strict = True
    id = datatypes.Function('validate_id', error='Invalid Id', )
    # action = datatypes.String(error='action must be a string')
    action = datatypes.Function('validate_action',error='action can be either add or  delete')

    def validate_action(self, val, **kwargs):
        if val == 'add' or val == 'delete':
            return True
        return False

    def validate_id(self, val, **kwargs):
        val = str(val)
        if val.isdigit() and 0 < len(val) < 15 and not val.__contains__(" "):
            return True
        return False


class IdValidator(PayloadValidator):
    strict = True

    id = datatypes.Function('validate_id', error='Invalid Id', )

    def validate_id(self, val, **kwargs):
        val = str(val)
        if val.isdigit() and 0 < len(val) < 15 and not val.__contains__(" "):
            return True
        return False


class PostValidator(PayloadValidator):
    strict = True

    post_pics = datatypes.Function('validatePostPic', required=False)
    text = datatypes.Function('validateText', error='Invalid characters present', required=False)

    def validateText(self, val, errors,*args, **kwargs):
        if val is None:
            return True
        elif 0 < len(str(val)) < 250 and not str(val).isspace():
            return True
        return False

    def validatePostPic(self, val, errors, *args,**kwargs):
        return True


class CommentValidator(PayloadValidator):
    strict = True
    id = datatypes.Function('validate_id', error='Invalid Id', )
    text = datatypes.Function('validateText', error='Invalid characters present', )

    def validateText(self, val, **kwargs):
        if val is None:
            return True
        elif 0 < len(str(val)) < 100 and not str(val).isspace():
            return True
        return False

    def validate_id(self, val, **kwargs):
        val = str(val)
        if val.isdigit() and 0 < len(val) < 15 and not val.__contains__(" "):
            return True
        return False


class PostUpdateValidator(PayloadValidator):
    strict = True

    id = datatypes.Function('validate_id', error='Invalid Id', )
    post_pics = datatypes.Function('validatePostPic', required=False)
    text = datatypes.Function('validateText', error='Invalid characters present', required=False)

    def validateText(self, val, errors, **kwargs):
        if val is None:
            return True
        elif 0 < len(str(val)) < 250 and not str(val).isspace():
            return True
        return False

    def validatePostPic(self, val, **kwargs):
        return True

    def validate_id(self, val, **kwargs):
        val=str(val)
        if val.isdigit() and 0 < len(val) < 15 and not val.__contains__(" "):
            return True
        return False


class RegisterValidate(PayloadValidator):
    strict = True

    password = datatypes.Function('validatePassword')
    country = datatypes.Function('validateCountry',
                                 error=('country can be either '
                                        'India, USA or Canada'))
    sex = datatypes.Function('validateSex',
                             error=('sex can be either '
                                    'male or  female'))
    first_name = datatypes.Function('validateFirstName')
    username = datatypes.Function('validateUsername')
    last_name = datatypes.Function('validateLastName')
    email = datatypes.Function('validateEmail', error="The Email provided is already registered !")
    city = datatypes.Function('validateCity',
                              error=('Invalid City'))
    profile_pic = datatypes.Function('validateProfilePic')

    def validateUsername(self, val, payload, errors, **kwargs):
        val=str(val)
        if not val.isalnum() or val.isdigit():
            errors.append("Username should be Alphanumeric")
            return False
        elif len(val) < 4:
            errors.append("Username length should be more than 4")
            return False
        elif len(val) > 14:
            errors.append("Username length should be less than 10")
            return False
        else:
            return True

    def validatePassword(self, val, payload, errors, **kwargs):
        val = str(val)
        if val.isalpha() or val.isdigit() or val.__contains__(" "):
            errors.append("Password should be atleast AlphaNumeric")
            return False
        elif len(val) < 4:
            errors.append("Password length should be more than 4")
            return False
        elif len(val) > 25:
            errors.append("Password length should be less than 25")
            return False
        else:
            return True

    def validateEmail(self, val, **kwargs):
        if validateUser.validateEmail(val):
            return False
        else:
            return True

    def validateSex(self, val, **kwargs):
        if val == 'male' or val == 'female':
            return True
        return False

    def validateCountry(self, val, **kwargs):
        if val == 'india' or val == 'usa' or val == 'canada':
            return True
        return False

    def validateCity(self, val, **kwargs):
        if val == 'mumbai' or val == 'delhi' or val == 'bangalore' or val == 'pune' or val == 'hyderabad' \
                or val == 'chennai' or val == 'kolkata' or val == 'mangalore' \
                or val == 'new york' or val == 'los angeles' or val == 'san francisco' or val == 'chicago' \
                or val == 'montreal' or val == 'sherbrooke' or val == 'toronto' or val == 'vancouver' \
                or val == 'halifax' or val == 'ottawa' or val == 'calgary':
            return True
        return False

    def validateFirstName(self, val, payload, errors, **kwargs):
        if not val.isalpha():
            errors.append("First Name should be Alphabets")
            return False
        elif len(val) < 4:
            errors.append("First Name length should be more than 4")
            return False
        elif len(val) > 10:
            errors.append("First Name length should be less than 10")
            return False
        else:
            return True

    def validateLastName(self, val, payload, errors, **kwargs):
        if not val.isalpha():
            errors.append("Last Name should be Alphabets")
            return False
        elif len(val) < 4:
            errors.append("Last Name length should be more than 4")
            return False
        elif len(val) > 10:
            errors.append("Last Name length should be less than 10")
            return False
        else:
            return True

    def validateProfilePic(self, val, **kwargs):
        return True


class RegisterUpdateValidate(PayloadValidator):
    strict = True
    country = datatypes.Function('validateCountry', error='country can be either India, USA or Canada', required=False)
    email = datatypes.Function('validateEmail', error="The Email provided is already registered !", required=False)
    city = datatypes.Function('validateCity', required=False, error='Invalid City')
    profile_pic = datatypes.Function('validateProfilePic', required=False)

    def validateEmail(self, val, **kwargs):
        val=str(val)
        if val or val != "sameEmail":
            if validateUser.validateEmail(val):
                return False
            else:
                return True
        else:
            return True

    def validateCountry(self, val, **kwargs, ):
        if val == 'india' or val == 'usa' or val == 'canada' or val is None:
            return True
        return False

    def validateCity(self, val, **kwargs):
        if val == 'mumbai' or val == 'delhi' or val == 'bangalore' or val == 'pune' or val == 'hyderabad' \
                or val == 'chennai' or val == 'kolkata' or val == 'mangalore' \
                or val == 'new york' or val == 'los angeles' or val == 'san francisco' or val == 'chicago' \
                or val == 'montreal' or val == 'sherbrooke' or val == 'toronto' or val == 'vancouver' \
                or val == 'halifax' or val == 'ottawa' or val == 'calgary' or val is None:
            return True
        return False

    def validateProfilePic(self, val, **kwargs):
        return True

class SearchValidate(PayloadValidator):
    strict = True
    input = datatypes.Function('validateInput')

    def validateInput(self, val, payload, errors, **kwargs):
        if not val.replace(" ", "").isalpha():
            errors.append("Input should be Alphabets")
            return False
        elif len(val) < 3:
            errors.append("Input length should be more than 3")
            return False
        elif len(val) > 25:
            errors.append("Input length should be less than 25")
            return False
        else:
            return True