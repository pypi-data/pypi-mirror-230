import os
import json
import random
from enum import Enum

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MALE_NAME_FILE = os.path.join(BASE_DIR, "male.json")
FEMALE_NAME_FILE = os.path.join(BASE_DIR, "female.json")


class SampleName:

    class Gender(Enum):
        '''
        性別
        '''
        All = 'All'
        Male = 'Male'
        Female = 'Female'

    class Language(Enum):
        '''
        JSON 的 key
        '''
        English = 'english'
        Chinese = 'chinese'

    def __init__(self, custom=None, length: int = 8):
        self._length = length
        self._loadNameList()
        self._customList = None
        if isinstance(custom, list):
            # 直接傳入 list[str] 作為自訂清單
            self._customList = custom
            self._lengthLimit(custom)
        elif isinstance(custom, str):
            # 載入 JSON 路徑檔案
            self._loadCustomFileList(custom)

    def _lengthLimit(self, checkList: list) -> None:
        '''
        限制 self._length 不要小於 list, 不然 random.sample() 會有錯誤
        '''
        if self._length > len(checkList):
            self._length = len(checkList)

    def _loadCustomFileList(self, filePath) -> None:
        '''
        載入自訂的 JSON list
        '''
        with open(filePath, 'r', encoding='utf-8') as file:
            self._customList = json.loads(file.read())
            self._lengthLimit(self._customList)

    def _loadNameList(self) -> None:
        '''
        instance 建立時載入名稱檔案, 不要每次呼叫 function 才讀取 JSON
        '''
        with open(MALE_NAME_FILE, 'r', encoding='utf-8') as file:
            self._male_name_list = json.loads(file.read())

        with open(FEMALE_NAME_FILE, 'r', encoding='utf-8') as file:
            self._female_name_list = json.loads(file.read())

    def _common_list_name(self,
                          gender: Gender,
                          language: Language,
                          length: int = None) -> list:
        '''
        listName 共用的 function
        '''
        if length is None:
            length = self._length
        if not (isinstance(length, int)):
            raise TypeError("length 須為 int")

        # 使用 random.sample 取得不重複的名稱
        if gender == self.Gender.Male:
            name_list = random.sample(self._male_name_list, length)
        elif gender == self.Gender.Female:
            name_list = random.sample(self._female_name_list, length)
        elif gender == self.Gender.All:
            name_list = random.sample(
                self._male_name_list + self._female_name_list, length)

        return [item[language.value] for item in name_list]

    def listCustom(self, length=None) -> list:
        '''
        從自訂的 list 隨機挑選不重複的
        '''
        if self._customList is None:
            raise NameError('自定義清單不存在')
        length = self._length if length is None else length

        if length > len(self._customList):
            raise ValueError(f'自訂清單長度小於 {length}')
        return random.sample(self._customList, length)

    def listNameEng(self, length: int = None) -> list:
        '''
        隨機取得男生/女生英文名字
        '''
        return self._common_list_name(self.Gender.All, self.Language.English,
                                      length)

    def listNameCht(self, length: int = None) -> list:
        '''
        隨機取得男生/女生英文名字翻譯
        '''
        return self._common_list_name(self.Gender.All, self.Language.Chinese,
                                      length)

    def listMaleNameEng(self, length: int = None) -> list:
        '''
        隨機取得男生英文名稱
        '''
        return self._common_list_name(self.Gender.Male, self.Language.English,
                                      length)

    def listMaleNameCht(self, length: int = None) -> list:
        '''
        隨機取得男生英文名字翻譯
        '''
        return self._common_list_name(self.Gender.Male, self.Language.Chinese,
                                      length)

    def listFemaleNameEng(self, length: int = None) -> list:
        '''
        隨機取得女生英文名字
        '''
        return self._common_list_name(self.Gender.Female,
                                      self.Language.English, length)

    def listFemaleNameCht(self, length: int = None) -> list:
        '''
        隨機取得女生英文名字翻譯
        '''
        return self._common_list_name(self.Gender.Female,
                                      self.Language.Chinese, length)
