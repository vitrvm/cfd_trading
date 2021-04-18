class Account(object):

    alias = None
    id = None
    name = None
    status = None
    accType = None
    balance = None
    currency = None

    class Type:
        CFD = 'CFD'
        PHYSICAL = 'PYSICAL'
        SPREADBET = 'SPREADBET'
        UNKNOWN = None

    def __init__(self) -> None:
        pass

class Accounts(object):

    accounts = []

    def __init__(self):
        pass

    def add_account(self, acc:Account):
        self.accounts.append(acc)

    def get_accounts(self):
        return self.accounts

    def get_account_by_id(self, id):
        if self.accounts is not None:    
            for acc in self.accounts:
                if id == acc.id:
                    return acc
        return None
        