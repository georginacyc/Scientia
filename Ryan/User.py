# Create class for accounts.
class User:
    countID = 0

    def __init__(self, firstName, lastName, email, password, bio, learn, teach):
        User.countID +=1
        self.__userID = User.countID
        self.__firstName = firstName
        self.__lastName = lastName
        self.__email = email
        self.__password = password
        self.__bio = bio
        self.__learn = learn
        self.__teach = teach

    def get_userID(self):
        return self.__userID
    def set_userID(self, userID):
        self.__userID = userID

    def get_firstName(self):
        return self.__firstName
    def set_firstName(self, firstName):
        self.__firstName = firstName

    def get_lastName(self):
        return self.__lastName
    def set_lastName(self, lastName):
        self.__lastName = lastName

    def get_email(self):
        return self.__email
    def set_email(self, email):
        self.__email = email

    def get_password(self):
        return self.__password
    def set_password(self, password):
        self.__password = password

    def get_bio(self):
        return self.__bio
    def set_bio(self, bio):
        self.__bio = bio

    def get_learn(self):
        return self.__learn
    def set_learn(self, learn):
        self.__learn = learn

    def get_teach(self):
        return self.__teach
    def set_teach(self, teach):
        self.__teach = teach
