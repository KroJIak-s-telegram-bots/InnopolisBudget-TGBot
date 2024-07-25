
from utils.funcs import joinPath

class configCategoryObject:
    def __init__(self, config, nameCategory):
        self.config = config
        self.nameCategory = nameCategory

    def get(self, elm):
        return self.config.get(self.nameCategory, elm)

class Telegram(configCategoryObject):
    def __init__(self, config):
        super().__init__(config, 'Telegram')
        self.token = self.get('token')
        self.alias = self.get('alias')

class Data(configCategoryObject):
    def __init__(self, config):
        super().__init__(config, 'Data')
        self.defaultLang = self.get('defaultLang')

class Logging:
    def __init__(self):
        self.format = '%(asctime)s %(levelname)s %(message)s'

class Path:
    def __init__(self):
        self.project = joinPath('/', *__file__.split('/')[:-2])
        self.cache = joinPath(self.project, 'cache')
        self.client = joinPath(self.project, 'client')
        self.config = joinPath(self.client, 'config')
        self.lang = joinPath(self.client, 'lang')
        self.logs = joinPath(self.client, 'logs')
        self.db = joinPath(self.project, 'db')
        self.users = joinPath(self.db, 'users')
        self.utils = joinPath(self.project, 'utils')
        self.objects = joinPath(self.utils, 'objects')

class File:
    def __init__(self):
        self.config = 'bot.ini'
        self.database = 'database.json'
        self.generalBudgetPdf = 'budget_general.pdf'

class Default:
    def __init__(self):
        self.parseMode = 'HTML'

class Callback:
    def __init__(self):
        self.codeadd = 'codeadd'
        self.coderemove = 'coderemove'
        self.list = 'list'

class Url:
    def __init__(self):
        self.innopolisHome = 'https://innopolis.university/'
        self.innopolisAdmission = self.innopolisHome + 'sveden/apply/?ysclid=lywwvn9v7v411071453'

class Parser:
    def __init__(self):
        self.tableNames = {0: 'Анализ данных и искусственный интеллект', 1: 'Инженерия информационных систем', 2: 'Математические основы искусственного интеллекта'}
        self.url = Url()

class ConstPlenty:
    def __init__(self, config=None):
        if config: self.addConstFromConfig(config)
        self.path = Path()
        self.default = Default()
        self.logging = Logging()
        self.file = File()
        self.callback = Callback()
        self.parser = Parser()

    def addConstFromConfig(self, config):
        self.telegram = Telegram(config)
        self.data = Data(config)