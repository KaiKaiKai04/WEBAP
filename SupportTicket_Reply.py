import random, string

class SupportTicket:
    def __init__(self, sender_email, receiver_email, subject, message):
        self.__support_id = self.__generate_ticket_number()
        self.__sender_email = sender_email
        self.__receiver_email = receiver_email
        self.__subject = subject
        self.__message = message

    def __generate_ticket_number(self):
        letters = ''.join(random.choices(string.ascii_lowercase, k=2))
        numbers = ''.join(random.choices(string.digits, k=4))
        return f"{letters}{numbers}"

    #Accessor methods
    def get_support_id(self):
        return self.__support_id
    def get_sender_email(self):
        return self.__sender_email
    def get_receiver_email(self):
        return self.__receiver_email
    def get_subject(self):
        return self.__subject
    def get_message(self):
        return self.__message

    #Mutator methods
    def set_user_id(self, support_id):
        self.__support_id = support_id
    def set_sender_email(self, sender_email):
        self.__sender_email = sender_email
    def set_receiver_email(self, receiver_email):
        self.__receiver_email = receiver_email
    def set_subject(self, subject):
        self.__subject = subject
    def set_message(self, message):
        self.__message = message



