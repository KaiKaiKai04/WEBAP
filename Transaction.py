class Transaction:
    count = 0
    def __init__(self, name, cc, user_id, pn, card_name, exp_date, cvc):
        Transaction.count += 1 # reset to 0 when server resets
        self.__tx_id = Transaction.count
        self.__user_id = user_id
        self.__name = name
        self.__product_name = None
        self.__cost = None
        self.__cc = cc
        self.__status = "Pending"
        self.__pn = pn
        self.__card_name = card_name
        self.__exp_date = exp_date
        self.__cvc = cvc

    def get_tx_id(self):
        return self.__tx_id
    
    def get_user_id(self):
        return self.__user_id

    def get_name(self):
        return self.__name

    def get_product_name(self):
        return self.__product_name

    def get_cost(self):
        return self.__cost
    
    def get_cc(self):
        return self.__cc
    
    def get_status(self):
        return self.__status
    
    def get_pn(self):
        return self.__pn
    
    def get_card_name(self):
        return self.__card_name
    
    def get_exp_date(self):
        return self.__exp_date
    
    def get_cvc(self):
        return self.__cvc

    # Mutator (setter) methods

    def set_tx_id(self, tx_id):
        self.__tx_id = tx_id

    def set_user_id(self, user_id):
        self.__user_id = user_id

    def set_name(self, name):
        self.__name = name
    
    def set_product_name(self, product_name):
        self.__product_name = product_name
    
    def set_cost(self, cost):
        self.__cost = cost

    def set_cc(self, cc):
        self.__cc = cc

    def set_status(self,status):
        self.__status = status
    
    def set_pn(self,pn):
        self.__pn = pn

    def set_card_name(self,card_name):
        self.__card_name = card_name

    def set_exp_date(self,exp_date):
        self.__exp_date = exp_date

    def set_cvc(self,cvc):
        self.__cvc = cvc