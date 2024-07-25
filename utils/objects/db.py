
class User:
    def __init__(self, userId, dictUser):
        self.userId = userId
        self.login = dictUser['login']
        self.fullname = dictUser['fullname']
        self.permission = dictUser['permission']
        self.code = dictUser['code']

    def isDefault(self):
        return self.permission == 'default'

    def isAdmin(self):
        return self.permission == 'admin'