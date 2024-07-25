
import json
import os

from utils.funcs import joinPath
from utils.const import ConstPlenty
from utils.objects.db import User

const = ConstPlenty()

class dbWorker():
    def __init__(self, databasePath):
        folderPath = databasePath.split('/')
        self.fileName = folderPath.pop(-1)
        self.folderPath = '/'.join(folderPath)
        if not self.isExists(): self.save({})

    def isExists(self):
        files = os.listdir(self.folderPath if len(self.folderPath) > 0 else None)
        return self.fileName in files

    def get(self):
        with open(joinPath(self.folderPath, self.fileName)) as file:
            dbData = json.load(file)
        return dbData

    def save(self, dbData):
        with open(joinPath(self.folderPath, self.fileName), 'w', encoding='utf-8') as file:
            json.dump(dbData, file, indent=4, ensure_ascii=False)

class dbLocalWorker():
    def __init__(self):
        self.db = {}

    def isUserExists(self, userId):
        return str(userId) in self.db

    def addNewUser(self, userId):
        self.db[str(userId)] = dict(mode=-1,
                                    removedMessageIds=[])

    def setUserMode(self, userId, mode):
        self.db[str(userId)]['mode'] = mode

    def getUserMode(self, userId):
        return self.db[str(userId)]['mode']

    def addRemovedMessageIds(self, userId, messageId):
        self.db[str(userId)]['removedMessageIds'].append(messageId)

    def getRemovedMessageIds(self, userId):
        return self.db[str(userId)]['removedMessageIds']

    def clearRemovedMessageIds(self, userId):
        self.db[str(userId)]['removedMessageIds'] = []

class dbUsersWorker(dbWorker):
    def getUserIds(self):
        dbData = self.get()
        userIds = tuple(dbData['users'].keys())
        return userIds

    def isUserExists(self, userId):
        dbData = self.get()
        return str(userId) in dbData['users']

    def addNewUser(self, userId, login, fullname, permission, code=None):
        dbData = self.get()
        newUser = dict(login=login,
                       fullname=fullname,
                       permission=permission,
                       code=code)
        dbData['users'][str(userId)] = newUser
        self.save(dbData)

    def getUser(self, userId):
        dbData = self.get()
        dictUser = dbData['users'][str(userId)]
        user = User(str(userId), dictUser)
        return user

    def setInUser(self, userId, key, value):
        dbData = self.get()
        dbData['users'][str(userId)][key] = value
        self.save(dbData)

    def setCodeInUser(self, userId, code):
        self.setInUser(userId, 'code', code)

    def getPermissions(self):
        dbData = self.get()
        permissions = tuple(dbData['permissions'].values())
        return permissions