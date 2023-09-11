# SampleName
產生隨機英文名稱

# 範例
```
from sampleName import SampleName

smapleName = SampleName()
nameList = smapleName.listNameEng()
print(nameList)
# ['Kate', 'Cedric', 'Adrian', 'Yuri', 'Lara', 'Mildred', 'Craig', 'Oswald']
nameList = smapleName.listNameCht()
print(nameList)
# ['海頓', '藍道夫', '吉羅德', '妮可拉', '阿爾瓦', '比尤萊', '伊蒂絲', '珀莉']
```
# Development

 - VSCode
 - Remote container, 參考 https://8loser.github.io/2022/05/13/Remote-Containers/
 - 執行 VSCode remote container 會自動安裝 flake8, yapf 套件, 以及 pytest
 