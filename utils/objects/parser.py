
class Applicant:
    def __init__(self, field: str, number: int, code: str, priority: int, sumPoints: float, individualAchievements: float, numberWithOriginal: int = None, approzimateNumber: int = None, isBvi=False, isOriginal=False, isGosUslugiOriginal=False):
        self.field = field
        self.number = number
        self.code = code
        self.priority = priority
        self.sumPoints = sumPoints
        self.individualAchievements = individualAchievements
        self.numberWithOriginal = numberWithOriginal
        self.approzimateNumber = approzimateNumber
        self.isBvi = isBvi
        self.isOriginal = isOriginal
        self.isGosUslugiOriginal = isGosUslugiOriginal

    def __str__(self):
        return f'[Applicant] field: {self.field} number: {self.number} code: {self.code} priority: {self.priority} sumPoints: {self.sumPoints} individualAchievements: {self.individualAchievements} numberWithOriginal: {self.numberWithOriginal} approzimateNumber: {self.approzimateNumber} isBvi: {self.isBvi} isOriginal: {self.isOriginal} isGosUslugiOriginal: {self.isGosUslugiOriginal}'
