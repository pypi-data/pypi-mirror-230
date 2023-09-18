# SampleName
[![PyPI](https://img.shields.io/pypi/v/SampleName?color=%2334D058&label=pypi%20package)](https://pypi.org/project/SampleName/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/SampleName.svg)](https://pypi.org/project/SampleName/)
![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/8loser/SampleName/push_test.yml)

產生隨機英文名稱或英文名稱的中文翻譯, 寫範例程式時可以用

# 名稱清單
 - [male.json](https://github.com/8loser/SampleName/blob/main/sampleName/male.json)
 - [female.json](https://github.com/8loser/SampleName/blob/main/sampleName/female.json)

# Install
```
pip install SampleName
```
# Methods
 - listCustom() - 從自訂清單隨機挑選不重複的
 - listNameEng() - 隨機取得男生/女生英文名字
 - listNameCht() - 隨機取得男生/女生英文名字翻譯
 - listMaleNameEng() - 隨機取得男生英文名稱
 - listMaleNameCht() - 隨機取得男生英文名字翻譯
 - listFemaleNameEng() - 隨機取得女生英文名字
 - listFemaleNameCht() - 隨機取得女生英文名字翻譯
# Using

## 建立物件
```
from sampleName import SampleName
smapleName = SampleName()
```

## 隨機取出 8 筆名稱 (預設 8 筆)
```
# 取出隨機男性/女性 英文 名稱
nameList = smapleName.listNameEng()
print(nameList)
# ['Kate', 'Cedric', 'Adrian', 'Yuri', 'Lara', 'Mildred', 'Craig', 'Oswald']

# 取出隨機男性/女性 中文 名稱
nameList = smapleName.listNameCht()
print(nameList)
# ['海頓', '藍道夫', '吉羅德', '妮可拉', '阿爾瓦', '比尤萊', '伊蒂絲', '珀莉']
```

## 隨機取出自訂筆數名稱
```
# 取出 4 筆女性英文名稱
nameList = smapleName.listFemaleNameEng(4)
print(nameList)
# ['Elizabeth', 'Irene', 'Candice', 'Myra']

# 取出 5 筆男性英文名稱翻譯
nameList = smapleName.listMaleNameCht(5)
print(nameList)
# ['班森', '愛格伯特', '扎威爾', '凱利', '菲力克斯']
```

## 從自訂清單內取得隨機名稱
```
nameList = ["愛爾默", "妮可拉", "特麗莎布藍達", "伯頓", "若娜"]
smapleName = SampleName(l)
nameList = smapleName.listCustom(2)
print(nameList)
# ['特麗莎布藍達', '愛爾默']
```

## 載入自訂名稱檔案
```
# nameList.json 內容
# ["愛爾默", "妮可拉", "特麗莎布藍達", "伯頓", "若娜"]
nameFile = 'nameList.json'
smapleName = SampleName(nameFile)
nameList = smapleName.listCustom(2)
print(nameList)
# ['妮可拉', '愛爾默']
```

# Development

 - VSCode
 - 開發環境佈置 [Remote-Containers](https://8loser.github.io/2022/05/13/Remote-Containers/)
   - 執行 remote container 會自動安裝 flake8, yapf 套件, 以及 pytest
 - 單元測試, 執行 `pytest`
   - [test_sampleName.py](https://github.com/8loser/SampleName/blob/main/tests/test_sampleName.py)
 - release 後會自動上傳到 PyPI, 版本號會用 tag
   - [release_action.yml](https://github.com/8loser/SampleName/blob/main/.github/workflows/release_action.yml)
   - [setup.py](https://github.com/8loser/SampleName/blob/main/setup.py)