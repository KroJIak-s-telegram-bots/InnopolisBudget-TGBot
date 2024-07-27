
from traceback import format_exc
import asyncio
import logging
import json
from fnmatch import fnmatch

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram import F

from utils.const import ConstPlenty
from utils.funcs import joinPath, getConfigObject, getLogFileName
from utils.database import dbUsersWorker, dbLocalWorker
from utils.objects.client import UserInfo, CallbackUserInfo
from utils.parser.main import getUserBudgetInfoListFromTable

const = ConstPlenty()
botConfig = getConfigObject(joinPath(const.path.config, const.file.config))
const.addConstFromConfig(botConfig)
# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO, filename=joinPath(const.path.logs, getLogFileName()), filemode='w', format=const.logging.format)
dbUsers = dbUsersWorker(joinPath(const.path.users, const.file.database))
dbLocal = dbLocalWorker()
bot = Bot(const.telegram.token, default=DefaultBotProperties(parse_mode=const.default.parseMode))
dp = Dispatcher()


def getTranslation(userInfo, key, inserts=[]):
    user = dbUsers.getUser(userInfo.userId)
    try:
        with open(joinPath(const.path.lang, f'{const.data.defaultLang}.json'), encoding='utf-8') as langFile:
            langJson = json.load(langFile)
        text = langJson[key]
        if not inserts: return text
        for ins in inserts: text = text.replace('%{}%', str(ins), 1)
        return text
    except Exception:
        if user.isAdmin(): return getTranslation(userInfo, 'error.message', [format_exc()])
        else: return getTranslation(userInfo, 'error.message', ['wwc'])

def getUserInfo(message):
    userInfo = UserInfo(message)
    if not dbUsers.isUserExists(userInfo.userId):
        permissions = dbUsers.getPermissions()
        dbUsers.addNewUser(userInfo.userId, userInfo.username, userInfo.userFullName, permissions[0])
    if not dbLocal.isUserExists(userInfo.userId):
        dbLocal.addNewUser(userInfo.userId)
    dbLocal.addRemovedMessageIds(userInfo.userId, userInfo.messageId)
    userLogInfo = f'{userInfo} | {dbLocal.db[str(userInfo.userId)]}'
    logging.info(userLogInfo)
    print(userLogInfo)
    return userInfo

async def removeLastMessageIds(userInfo):
    if not dbLocal.isUserExists(userInfo.userId): dbLocal.addNewUser(userInfo.userId)
    messageIdsList = dbLocal.getRemovedMessageIds(userInfo.userId)
    for messageId in messageIdsList:
        await bot.delete_message(userInfo.chatId, messageId)
    dbLocal.clearRemovedMessageIds(userInfo.userId)

def getMainKeyboard(userInfo):
    inlineButtons = []
    user = dbUsers.getUser(userInfo.userId)
    if user.code is None:
        inlineButtons.append([types.InlineKeyboardButton(text=getTranslation(userInfo, 'button.code.add'), callback_data=const.callback.codeadd)])
    else:
        inlineButtons.append([types.InlineKeyboardButton(text=getTranslation(userInfo, 'button.code.remove'), callback_data=const.callback.coderemove)])
        inlineButtons.append([types.InlineKeyboardButton(text=getTranslation(userInfo, 'button.list'), callback_data=const.callback.list)])
    inlineKeyboard = types.InlineKeyboardMarkup(inline_keyboard=inlineButtons)
    return inlineKeyboard

@dp.message(Command('start'))
async def startHandler(message: types.Message):
    userInfo = getUserInfo(message)
    dbLocal.setUserMode(userInfo.userId, 0)
    await removeLastMessageIds(userInfo)
    mainKeyboard = getMainKeyboard(userInfo)
    botMessage = await message.answer(getTranslation(userInfo, 'start.message', [userInfo.userFirstName]), reply_markup=mainKeyboard)
    dbLocal.addRemovedMessageIds(userInfo.userId, botMessage.message_id)

@dp.callback_query(F.data == const.callback.codeadd)
async def codeAddCallback(callback: types.CallbackQuery):
    userInfo = CallbackUserInfo(callback)
    dbLocal.setUserMode(userInfo.userId, 1)
    await removeLastMessageIds(userInfo)
    botMessage = await callback.message.answer(getTranslation(userInfo, 'code.message.add'))
    dbLocal.addRemovedMessageIds(userInfo.userId, botMessage.message_id)

def checkUserCode(text):
    return fnmatch(text, '???-???-??? ??')

async def setUserCodeHandler(userInfo, message):
    if not checkUserCode(userInfo.userText):
        botMessage = await message.answer(getTranslation(userInfo, 'code.message.failed'))
        dbLocal.addRemovedMessageIds(userInfo.userId, botMessage.message_id)
        return
    dbUsers.setCodeInUser(userInfo.userId, userInfo.userText)
    dbLocal.setUserMode(userInfo.userId, 0)
    await removeLastMessageIds(userInfo)
    mainKeyboard = getMainKeyboard(userInfo)
    botMessage = await message.answer(getTranslation(userInfo, 'success.message'), reply_markup=mainKeyboard)
    dbLocal.addRemovedMessageIds(userInfo.userId, botMessage.message_id)

@dp.callback_query(F.data == const.callback.coderemove)
async def codeRemoveCallback(callback: types.CallbackQuery):
    userInfo = CallbackUserInfo(callback)
    dbUsers.setCodeInUser(userInfo.userId, None)
    await removeLastMessageIds(userInfo)
    mainKeyboard = getMainKeyboard(userInfo)
    botMessage = await callback.message.answer(getTranslation(userInfo, 'success.message'), reply_markup=mainKeyboard)
    dbLocal.addRemovedMessageIds(userInfo.userId, botMessage.message_id)

@dp.callback_query(F.data == const.callback.list)
async def getListCallback(callback: types.CallbackQuery):
    userInfo = CallbackUserInfo(callback)
    await removeLastMessageIds(userInfo)
    user = dbUsers.getUser(userInfo.userId)
    budgetInfoList = getUserBudgetInfoListFromTable(user.code)
    if len(budgetInfoList) == 0:
        mainKeyboard = getMainKeyboard(userInfo)
        botMessage = await callback.message.answer(getTranslation(userInfo, 'list.message.empty'), reply_markup=mainKeyboard)
        dbLocal.addRemovedMessageIds(userInfo.userId, botMessage.message_id)
        return
    botMessage = await callback.message.answer(getTranslation(userInfo, 'list.message.found', [len(budgetInfoList)]))
    dbLocal.addRemovedMessageIds(userInfo.userId, botMessage.message_id)
    for index, applicant in enumerate(budgetInfoList):
        isBvi = '✅' if applicant.isBvi else '❌'
        isOriginal = '✅' if applicant.isOriginal else '❌'
        isGosUslugiOriginal = '✅' if applicant.isGosUslugiOriginal else '❌'
        mainKeyboard = getMainKeyboard(userInfo) if index == len(budgetInfoList) - 1 else None
        botMessage = await callback.message.answer(getTranslation(userInfo, 'list.message.info', [applicant.field, applicant.number, applicant.numberWithOriginal, applicant.approzimateNumber,
                                                                                                            applicant.priority, applicant.sumPoints, applicant.individualAchievements,
                                                                                                            isBvi, isOriginal, isGosUslugiOriginal]), reply_markup=mainKeyboard)
        dbLocal.addRemovedMessageIds(userInfo.userId, botMessage.message_id)

def isUnknownCommand(userInfo):
    return userInfo.userText and userInfo.userText[0] == '/'

async def unknownCommandHandler(userInfo, message):
    await removeLastMessageIds(userInfo)
    mainKeyboard = getMainKeyboard(userInfo)
    botMessage = await message.answer(getTranslation(userInfo, 'unknown.command.message'), reply_markup=mainKeyboard)
    dbLocal.addRemovedMessageIds(userInfo.userId, botMessage.message_id)

@dp.message()
async def mainHandler(message: types.Message):
    userInfo = getUserInfo(message)
    userMode = dbLocal.getUserMode(userInfo.userId)

    if isUnknownCommand(userInfo):
        await unknownCommandHandler(userInfo, message)
        return
    else:
        match userMode:
            case 1: await setUserCodeHandler(userInfo, message)

async def mainTelegram():
    await dp.start_polling(bot)

def main():
    asyncio.run(mainTelegram())

if __name__ == '__main__':
    main()