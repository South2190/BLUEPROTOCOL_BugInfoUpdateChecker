import datetime
import glob
import json
import os
import requests
import sys

JsonDirectoryName = "json"
JsonFileNamePattern = "bug-report-????????.json"
JsonGetUrl = "https://object-web.blue-protocol.com/bug-report.json"

def ExtContent(content):
	text = ""
	for item in content:
		match item["type"]:
			case "paragraph":
				for li in item["data"]["text"].split("<br>"):
					if li != "":
						#print(li)
						text += li + '\n'
			case "list":
				for li in item["data"]["items"]:
					#print("- ", end = "")
					text += "- "
					for line in li.split("<br>"):
						if line != "":
							#print(line)
							text += line + '\n'
			case "delimiter":
				#print("---------------------------------------------")
				text += "---------------------------------------------\n"
			case "b_link":
				for dt in item["data"]["content"]["data"]:
					#print("[{}](<{}>)".format(dt["text"], dt["url"]))
					text += "[{}](<{}>)\n".format(dt["text"], dt["url"])
			case "image":
				for dt in item["data"]["content"]["data"]:
					#print(dt["url"])
					text += dt["url"] + '\n'
	return text

# 2つの数字を比較し表示
def PrintNumber(text, num1, num2):
	print(f"{text}: ", end = "")
	Diff = num2 - num1
	if Diff == 0:
		print(num1)
	else:
		print(f"{num1} -> {num2} (差分: {Diff})")

os.chdir(f"{os.path.dirname(os.path.abspath(__file__))}/{JsonDirectoryName}")

if len(sys.argv) <= 1:
	Latest = 0
	for date in glob.glob(JsonFileNamePattern):
		if Latest < int(date[11:19]):
			Latest = int(date[11:19])
	OldJsonFileName = f"bug-report-{Latest}.json"
else:
	OldJsonFileName = os.path.basename(sys.argv[1])
print(OldJsonFileName)

# 過去の不具合情報をJSONファイルから読み込む
with open(OldJsonFileName, 'r', encoding = "utf-8") as f:
	OldJson = {x["bugReportId"]: x for x in json.load(f)}

# 最新の不具合情報をサーバーから取得
PlaneJson = requests.get(JsonGetUrl).json()
NewJson = {x["bugReportId"]: x for x in PlaneJson}

# 不具合情報が更新されていない場合は終了
if OldJson == NewJson:
	print("不具合情報の更新はありません")
	exit()

Old = OldJson.keys()
New = NewJson.keys()

# 今回追加された不具合情報の抽出
print("\n# 今回追加された不具合情報")
for x in New - Old:
	print("1. [{}](<https://blue-protocol.com/support/bug-report/{}>)".format(NewJson[x]["title"], x))

# 今回削除された不具合情報の抽出
"""print("\n# 今回削除された不具合情報")
for x in Old - New:
	print("1. [{}](<https://blue-protocol.com/support/bug-report/{}>)".format(OldJson[x]["title"], x))"""

# カテゴリ変更の抽出
CatName = ["対応中", "対応済", "仕様"]
OldCat = [set(), set(), set()]
NewCat = [set(), set(), set()]
Common = set()

# bugReportCategoryIdを基準にbugReportIdを分類
for x in Old & New:
	OldCat[OldJson[x]["bugReportCategory"]["bugReportCategoryId"] - 2].add(x)
	NewCat[NewJson[x]["bugReportCategory"]["bugReportCategoryId"] - 2].add(x)

# 対応状況が変更された不具合情報の抽出
print("\n# 対応状況が更新された不具合情報")
for (OldCatItem, NewCatItem, OldCatName) in zip(OldCat, NewCat, CatName):
	for item in OldCatItem - NewCatItem:
		print("1. [{}](<https://blue-protocol.com/support/bug-report/{}>) (__**{}**__ -> __**{}**__)".format(NewJson[item]["title"], item, OldCatName, NewJson[item]["bugReportCategory"]["displayName"]))
	Common |= OldCatItem & NewCatItem

print("\n# 内容が更新された不具合情報")
for x in Common:
	if OldJson[x]["platform"] != NewJson[x]["platform"]:
		print("1. [{}](<https://blue-protocol.com/support/bug-report/{}>) ※対象プラットフォーム".format(NewJson[x]["title"], x))
	if OldJson[x]["title"] != NewJson[x]["title"]:
		print("1. [{}](<https://blue-protocol.com/support/bug-report/{}>)".format(NewJson[x]["title"], x))
	elif ExtContent(OldJson[x]["content"]) != ExtContent(NewJson[x]["content"]):
		print("1. [{}](<https://blue-protocol.com/support/bug-report/{}>)".format(NewJson[x]["title"], x))
	"""elif OldJson[x]["content"] != NewJson[x]["content"]:
		print("1. [{}](<https://blue-protocol.com/support/bug-report/{}>) (content)".format(NewJson[x]["title"], x))
	elif OldJson[x] != NewJson[x]:
		print("1. [{}](<https://blue-protocol.com/support/bug-report/{}>) (要素全体)".format(NewJson[x]["title"], x))"""

# 統計情報の収集
print("\n# 統計情報")
OldCatTotal = [0, 0, 0]
for x in Old:
	OldCatTotal[OldJson[x]["bugReportCategory"]["bugReportCategoryId"] - 2] += 1
NewCatTotal = [0, 0, 0]
for x in New:
	NewCatTotal[NewJson[x]["bugReportCategory"]["bugReportCategoryId"] - 2] += 1

for x in range(3):
	PrintNumber(f"{CatName[x]}の件数", OldCatTotal[x], NewCatTotal[x])
PrintNumber("合計", len(Old), len(New))
MaxInOld = 0
for x in Old:
	if MaxInOld <= x:
		MaxInOld = x
MaxInNew = 0
for x in New:
	if MaxInNew <= x:
		MaxInNew = x
BlankIdCount = 0
for x in range(MaxInOld + 1, MaxInNew + 1):
	if x not in NewJson:
		BlankIdCount += 1

print("\n！！！！！！！！！！　Danger Zone　！！！！！！！！！！")
PrintNumber("ID最大値", MaxInOld, MaxInNew)
OldBlankIdCnt = MaxInOld - len(Old)
NewBlankIdCnt = MaxInNew - len(New)
PrintNumber("使用されていないIDの数", OldBlankIdCnt, NewBlankIdCnt)
print(f"ID最大値の差分範囲内で使用されていないIDの数: {BlankIdCount}")

# 今回削除された不具合情報の抽出
print("\n# 今回削除された不具合情報")
for x in Old - New:
	print(f"[__**{OldJson[x]["bugReportCategory"]["displayName"]}**__]")
	print("[{}](<https://blue-protocol.com/support/bug-report/{}>)\n".format(OldJson[x]["title"], x))
	print(ExtContent(OldJson[x]["content"]))
	print("")

# 最新の不具合情報を保存
if input("最新のJSONファイルを保存しますか?(y/n)>") == 'y':
	filename = "bug-report-{}.json".format(datetime.date.today().strftime('%Y%m%d'))
	with open(filename, 'w', encoding = "utf-8") as f:
		json.dump(PlaneJson, f, indent = 4, ensure_ascii = False)
	print(f"ファイル名 \"{filename}\" として保存しました")