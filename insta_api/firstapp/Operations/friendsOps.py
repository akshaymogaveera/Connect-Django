from firstapp.Operations import validation
from firstapp.models import User, Friends


class FriendOperations:

    @staticmethod
    def addFriend(user1, user2):
        statusCode = None
        myResponse = None

        try:

            status12 = Friends.objects.filter(user1=user1, user2=user2).exists()
            status21 = Friends.objects.filter(user1=user2, user2=user1).exists()

            # If both Row exits 1>2 and 2>1
            if status12 and status21:
                friendstat12 = Friends.objects.get(user1=user1, user2=user2)
                friendstat21 = Friends.objects.get(user1=user2, user2=user1)

                if friendstat12.friend_status == 2 and friendstat21.friend_status == 2:
                    statusCode = 101
                    myResponse = " Already Friends"
                    print("Friends Already")
                elif friendstat12.friend_status != 2 and friendstat21.friend_status == 2:
                    friendstat12.friend_status = 2
                    friendstat12.save()
                    statusCode = 104
                    myResponse = " Friend status from 2>1 was already 2 so changed Friend status from 1>2 to 2"
                    print("2>1=2 so changed 1>2=2")
                elif friendstat21.friend_status != 2 and friendstat12.friend_status == 2:
                    friendstat21.friend_status = 2
                    friendstat21.save()
                    statusCode = 104
                    myResponse = " Friend status from 1>2 was already 2 so changed Friend status from 2>1 to 2"
                    print("1>2=2 so changed 2>1=2")
                else:
                    friendstat12.delete()
                    friendstat21.delete()
                    statusCode = 103
                    myResponse = " Unusual row was present, so deleted the row"
                    print("if none of the friend status is 2 delete both the rows")

            # if only row 1>2 exists
            elif status12:
                print("status12")
                friend12 = Friends.objects.get(user1=user1, user2=user2)
                if friend12.friend_status == 2:
                    statusCode = 103
                    myResponse = " Friend status from 1>2 was already 2 and no row existed from 2>1, so deleted row 1>2"
                    friend12.delete()

                elif friend12.friend_status == 0:
                    # add stat =1 user1>2
                    statusCode = 100
                    myResponse = "Friend Request sent - Friend status from 1>2 was 0 so changed Friend status from 1>2 to 1"
                    friend12.friend_status = 1
                    friend12.save()


                elif friend12.friend_status == 1:
                    # frnd req already sent from 1>2
                    statusCode = 105
                    myResponse = " Request Already sent"
                    print("req already sent")
                else:
                    # deleter row
                    friend12.delete()
                    statusCode = 103
                    myResponse = " Unusual row was present, so deleted the row"

            elif status21:
                friend21 = Friends.objects.get(user1=user2, user2=user1)
                if friend21.friend_status == 2:
                    # delter or add another connection as frnd
                    statusCode = 103
                    myResponse = " Friend status from 2>1 was already 2 and no row existed from 1>2, so deleted row 2>1"
                    friend21.delete()
                elif friend21.friend_status == 1:
                    # frnd req already sent from by 2>1 so accept req
                    friend21.friend_status = 2
                    friend21.save()
                    Friends.objects.get_or_create(user1=user1, user2=user2, friend_status=2)
                    statusCode = 102
                    myResponse = " Friend Request Accepted "

                else:
                    friend21.delete()
                    # deleter row
                    statusCode = 103
                    myResponse = " Unusual row was present, so deleted the row"

            elif not status12 and not status21:
                print("Create row 1>2=1")
                Friends.objects.get_or_create(user1=user1, user2=user2, friend_status=1)
                # request sent from 1 to 2
                statusCode = 100
                myResponse = "Friend Request sent "

            return statusCode, myResponse
        except Exception as e:
            print(e)
            return 201, str(e)

    @staticmethod
    def deleteFriend(user1, user2):

        statusCode = None
        myResponse = None

        try:
            status12 = Friends.objects.filter(user1=user1, user2=user2).exists()
            status21 = Friends.objects.filter(user1=user2, user2=user1).exists()

            # If both Row exits 1>2 and 2>1
            if status12 and status21:
                friendstat12 = Friends.objects.get(user1=user1, user2=user2)
                friendstat21 = Friends.objects.get(user1=user2, user2=user1)
                friendstat12.delete()
                friendstat21.delete()
                statusCode = 301
                myResponse = "Success"

            # if only row 1>2 exists
            elif status12:
                print("status12")
                friend12 = Friends.objects.get(user1=user1, user2=user2)
                statusCode = 303
                myResponse = "Success : Friend status from 1>2 was present and no row existed from 2>1, so deleted row 1>2"
                friend12.delete()

            else:
                statusCode = 300
                myResponse = " Sorry, they weren't friends or No friend request from 1>2 ! "

            return statusCode, myResponse
        except Exception as e:
            print(e)
            return 201, str(e)
