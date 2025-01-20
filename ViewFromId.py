import json
import os
import re
import sys

JsonDirectoryName = "json"

"""def ViewContent(content):
	for item in content:
		match item["type"]:
			case "paragraph":
				for li in item["data"]["text"].split("<br>"):
					if li != "":
						print(li)
			case "list":
				for li in item["data"]["items"]:
					print("- ", end = "")
					for line in li.split("<br>"):
						if line != "":
							#print(line.replace("<span class=\"txt--bold\">", "**").replace("</span>", "**"))
							print(line)
			case "delimiter":
				print("---------------------------------------------")
			case "b_link":
				for dt in item["data"]["content"]["data"]:
					print("[{}](<{}>)".format(dt["text"], dt["url"]))
			case "image":
				for dt in item["data"]["content"]["data"]:
					print(dt["url"])"""

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

if len(sys.argv) <= 1:
	FilePath = input("対象ファイル>")
else:
	FilePath = sys.argv[1]

TargetId = int(input("bugReportId>"))

with open(FilePath, 'r', encoding = "utf-8") as f:
	Json = json.load(f)

for x in Json:
	if x["bugReportId"] == TargetId:
		print(f"# `{os.path.basename(FilePath)}`での内容\n")
		print(f"[__**{x["bugReportCategory"]["displayName"]}**__]")
		print(f"## {x["title"]}")
		#ViewContent(x["content"])
		print(ExtContent(x["content"]))
		print("")
		print(x["content"])
		break