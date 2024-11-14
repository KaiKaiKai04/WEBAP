import random, string

class SupportTicket:
    def __init__(self, first_name, last_name, email, subject, message):
        self.__support_id = self.__generate_ticket_number()
        self.__first_name = first_name
        self.__last_name = last_name
        self.__email = email
        self.__subject = subject
        self.__message = message
        self.__status = 'Pending'

    def __generate_ticket_number(self):
        letters = ''.join(random.choices(string.ascii_lowercase, k=2))
        numbers = ''.join(random.choices(string.digits, k=4))
        return f"{letters}{numbers}"

    #Accessor methods
    def get_support_id(self):
        return self.__support_id
    def get_first_name(self):
        return self.__first_name
    def get_last_name(self):
        return self.__last_name
    def get_email(self):
        return self.__email
    def get_subject(self):
        return self.__subject
    def get_message(self):
        return self.__message
    def get_status(self):
        return self.__status

    #Mutator methods
    def set_user_id(self, support_id):
        self.__support_id = support_id
    def set_first_name(self, first_name):
        self.__first_name = first_name
    def set_last_name(self, last_name):
        self.__last_name = last_name
    def set_email(self, email):
        self.__email = email
    def set_subject(self, subject):
        self.__subject = subject
    def set_message(self, message):
        self.__message = message
    def set_status(self, status):
        self.__status = status



