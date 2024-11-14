class User():
    count = 0

    def __init__(self, name, email, password, admin = 0):
        User.count += 1  # reset to 0 when server resets
        self.__id = User.count
        self.__name = name
        self.__email = email
        self.__password = password
        self.__admin = admin

    def get_id(self):
        return self.__id

    # Getter and setter for name
    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    # Getter and setter for email
    def get_email(self):
        return self.__email

    def set_email(self, email):
        self.__email = email

    # Getter and setter for password
    def get_password(self):
        return self.__password

    def set_password(self, password):
        self.__password = password

    # Getter and setter for admin
    def get_admin(self):
        return self.__admin

    def set_admin(self, admin):
        self.__admin = admin
