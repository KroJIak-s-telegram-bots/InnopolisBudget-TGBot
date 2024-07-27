
from copy import copy

from utils.funcs import joinPath
from utils.const import ConstPlenty
from utils.objects.parser import Applicant

from bs4 import BeautifulSoup
import requests
import tabula

const = ConstPlenty()

def saveGeneralBudgetPdf(pdfPath):
    response = requests.get(const.parser.url.innopolisAdmission)
    soup = BeautifulSoup(response.text, 'lxml')
    result = soup.find_all('a', class_='block-thirteen__document-link show')
    generalBudgetObject = result[0]
    generalBudgetEndPoint = generalBudgetObject.get('href')
    innopolisGeneralBudgetUrl = const.parser.url.innopolisHome + generalBudgetEndPoint
    response = requests.get(innopolisGeneralBudgetUrl)
    with open(pdfPath, 'wb') as file:
        file.write(response.content)

def getTabulaTables(pdfPath):
    tabulaTables = tabula.read_pdf(pdfPath, pages='all', multiple_tables=True, pandas_options={'header': None})
    return tabulaTables

def getInnopolisTables(tabulaTables):
    innopolisTables = {}
    lastNumber = -1
    tableIndex = 0
    countOriginal = 0

    for table in tabulaTables:
        for _, row in table.iterrows():
            line = row.to_list()
            try: number = int(float(str(line[0]).replace(',', '.')))
            except: continue
            code, priority, isBvi, bviStatus, bviBased, sumPoints, bviRanking, individualAchievements, isOriginal, isGosUslugiOriginal = line[1:11]
            priority = int(priority)
            isBvi = True if isinstance(isBvi, str) else False
            sumPoints = float(sumPoints)
            bviRanking = float(str(bviRanking).replace(',', '.'))
            sumPoints = bviRanking if isBvi else sumPoints
            individualAchievements = int(individualAchievements)
            isOriginal = True if isinstance(isOriginal, str) else False
            isGosUslugiOriginal = True if isinstance(isGosUslugiOriginal, str) else False

            if number < lastNumber:
                tableIndex += 1
                countOriginal = 0
            tableName = const.parser.tableNames[tableIndex]
            if len(innopolisTables) <= tableIndex: innopolisTables[tableName] = []
            newApplicant = Applicant(tableName, number, code, priority, sumPoints, individualAchievements, numberWithOriginal=countOriginal + 1,
                                     isBvi=isBvi, isOriginal=isOriginal, isGosUslugiOriginal=isGosUslugiOriginal)
            innopolisTables[tableName].append(newApplicant)
            lastNumber = number
            if isOriginal or isGosUslugiOriginal: countOriginal += 1
    return innopolisTables

def getUserBudgetInfoListFromTable(userCode):
    pdfPath = joinPath(const.path.cache, const.file.generalBudgetPdf)
    saveGeneralBudgetPdf(pdfPath)
    tabulaTables = getTabulaTables(pdfPath)
    innopolisTables = getInnopolisTables(tabulaTables)
    budgetInfoList = []
    for name, field in innopolisTables.items():
        for index, applicant in enumerate(field):
            if applicant.code != userCode and (not (applicant.isOriginal or applicant.isGosUslugiOriginal) or applicant.priority > 1):
                innopolisTables[name][index] = None
        innopolisTables[name] = [elm for elm in innopolisTables[name] if elm is not None]
    for name, field in innopolisTables.items():
        for index, applicant in enumerate(field):
            userApplicant = copy(applicant)
            userApplicant.approzimateNumber = index + 1
            if applicant.code == userCode:
                budgetInfoList.append(userApplicant)
    return budgetInfoList

def getTotalPlaceInBudgetInfoList(userCode):
    pdfPath = joinPath(const.path.cache, const.file.generalBudgetPdf)
    saveGeneralBudgetPdf(pdfPath)
    tabulaTables = getTabulaTables(pdfPath)
    innopolisTables = getInnopolisTables(tabulaTables)
    totalOriginalDict = {}
    for name, field in innopolisTables.items():
        for index, applicant in enumerate(field):
            if applicant.code == userCode or applicant.isOriginal or applicant.isGosUslugiOriginal:
                if applicant.code not in totalOriginalDict or applicant.priority < totalOriginalDict[applicant.code].priority:
                    totalOriginalDict[applicant.code] = applicant
    totalOriginalList = sorted(totalOriginalDict.values(), key=lambda applicant: applicant.sumPoints, reverse=True)
    totalPlace = None
    for index, applicant in enumerate(totalOriginalList):
        if applicant.code == userCode: totalPlace = index
    return totalPlace